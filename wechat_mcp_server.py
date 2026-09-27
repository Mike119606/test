"""微信聊天记录 MCP Server (stdio 模式)。

基于 chatlog-keeper 的解密能力 + 已缓存的数据库密钥，提供对话式查询：
  - list_conversations : 列出会话（群/私聊、消息数）
  - get_messages       : 读取指定会话最近 N 天的消息
  - search_messages    : 按关键词搜索最近 N 天消息
  - status             : 密钥/数据库状态

仅读取本人本机微信数据库，不做任何写入或上传。
"""
import io
import json
import os
import sys
import time
import traceback

BASE = r"c:\Users\应轩旸\Documents\trae_projects\001"
PKG = os.path.join(BASE, "chatlog-keeper", "chatlog-keeper-main")

os.environ.setdefault("CHATLOG_KEEPER_DATA_DIR", os.path.join(BASE, "keeper-data"))
os.environ.setdefault("CHATLOG_WECHAT_DATA_ROOT", r"E:\微信\微信聊天记录\xwechat_files")

sys.path.insert(0, PKG)
try:  # embeddable python 需要 reconfigure 保证 stdio UTF-8
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from chatlog_keeper.wechat_db import WeChatDBReader  # noqa: E402

# 非文本消息类型标记
TYPE_MAP = {3: "[图片]", 34: "[语音]", 43: "[视频]", 47: "[表情包]", 48: "[位置]",
            49: "[链接/文件]", 51: "[状态]", 10000: "[系统]", 10002: "[撤回]"}
MAX_CONTENT_CHARS = 300
READER = None


def get_reader():
    global READER
    if READER is None:
        READER = WeChatDBReader()
        READER.initialize()
    return READER


def directory():
    rd = get_reader()
    try:
        entries = rd.read_conversation_directory()
    except Exception as exc:
        entries = None
        sys.stderr.write(f"directory error: {exc}\n")
    return entries or []


def resolve_chat(name_or_id):
    """把用户传入的会话名/ID 解析为 conversation_id。返回 (id, error)。"""
    if not name_or_id:
        return None, "缺少会话名称。先调用 list_conversations 查看可用会话。"
    key = str(name_or_id).strip()
    entries = directory()
    if not entries:
        return None, "无法读取会话目录（密钥或数据库不可用），可先调用 status 检查。"
    if key.endswith("@chatroom") or "@" in key:
        for e in entries:
            if e["conversation_id"] == key:
                return key, None
    hits = [e for e in entries if key in e.get("label", "") or key in e["conversation_id"]]
    if len(hits) == 1:
        return hits[0]["conversation_id"], None
    if len(hits) > 1:
        top = sorted(hits, key=lambda x: x.get("message_count", 0), reverse=True)[:8]
        listing = "\n".join(f"- {e['label']} ({e['conversation_id']}, {e['message_count']}条)"
                            for e in top)
        return None, "匹配到多个会话，请用更精确的名称或直接指定 id：\n" + listing
    return None, f"未找到会话「{key}」。请先调用 list_conversations 查看会话列表。"


def fmt_message(m):
    t = m.timestamp.strftime("%Y-%m-%d %H:%M")
    sender = (m.sender_display_name or m.sender or "?").strip()
    content = (m.content or "").replace("\n", " ").strip()
    if m.msg_type != 1:
        content = TYPE_MAP.get(m.msg_type, f"[type={m.msg_type}]") + \
            (" " + content if content and m.msg_type in (10000, 49) else "")
    if len(content) > MAX_CONTENT_CHARS:
        content = content[:MAX_CONTENT_CHARS] + "…"
    return f"[{t}] {sender}: {content}"


def tool_status(_args):
    rd = get_reader()
    return {
        "initialized": bool(rd._initialized),
        "account_id": rd.account_id,
        "wxid_dir": str(rd.wxid_dir) if rd.wxid_dir else None,
        "dbs_unlocked": len(rd.enc_keys),
        "conversations": len(directory()),
    }


def tool_list_conversations(args):
    entries = directory()
    keyword = str(args.get("filter") or "").strip()
    only_groups = bool(args.get("groups_only"))
    if only_groups:
        entries = [e for e in entries if e.get("conversation_type") == "group"]
    if keyword:
        entries = [e for e in entries
                   if keyword in e.get("label", "") or keyword in e["conversation_id"]]
    entries = sorted(entries, key=lambda x: x.get("message_count", 0), reverse=True)
    limit = min(int(args.get("limit") or 100), 500)
    lines = [f"{e['label']} | {e['conversation_type']} | {e['message_count']}条 | {e['conversation_id']}"
             for e in entries[:limit]]
    return {"total_matched": len(entries), "shown": min(len(entries), limit),
            "conversations": lines}


def tool_get_messages(args):
    cid, err = resolve_chat(args.get("chat"))
    if err:
        return {"error": err}
    days = max(1, min(int(args.get("days") or 7), 30))
    limit = max(1, min(int(args.get("limit") or 2000), 5000))
    until = time.time()
    since = until - days * 86400
    rd = get_reader()
    msgs = rd.read_after(since, chat_name=cid, until_ts=until)
    msgs = msgs[-limit:]
    lines = [fmt_message(m) for m in msgs if (m.content or "").strip() or m.msg_type not in (1,)]
    return {"chat": cid, "days": days, "count": len(lines),
            "messages": lines}


def tool_search_messages(args):
    keyword = str(args.get("keyword") or "").strip()
    if not keyword:
        return {"error": "缺少 keyword 参数"}
    days = max(1, min(int(args.get("days") or 7), 30))
    limit = max(1, min(int(args.get("limit") or 200), 500))
    cid, err = resolve_chat(args.get("chat")) if args.get("chat") else (None, None)
    if err:
        return {"error": err}
    until = time.time()
    since = until - days * 86400
    rd = get_reader()
    msgs = rd.read_after(since, chat_name=cid, until_ts=until)
    hits = []
    for m in msgs:
        content = (m.content or "").strip()
        if not content:
            continue
        text = content if m.msg_type == 1 else TYPE_MAP.get(m.msg_type, "") + " " + content
        if keyword.lower() in text.lower():
            hits.append(fmt_message(m))
    hits = hits[-limit:]
    return {"keyword": keyword, "days": days, "count": len(hits), "messages": hits}


TOOLS = [
    {
        "name": "list_conversations",
        "description": "列出本机微信的会话列表（群聊/私聊、消息总数）。用 filter 按名称过滤。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filter": {"type": "string", "description": "按会话名称/ID 子串过滤"},
                "groups_only": {"type": "boolean", "description": "仅显示群聊"},
                "limit": {"type": "integer", "description": "最多返回条数，默认100"}
            }
        }
    },
    {
        "name": "get_messages",
        "description": "读取指定会话最近 N 天的消息记录（时间正序）。chat 支持会话名称（如群名）或 @chatroom id。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chat": {"type": "string", "description": "会话名称或 conversation_id"},
                "days": {"type": "integer", "description": "回看天数，默认7，最大30"},
                "limit": {"type": "integer", "description": "最多返回条数，默认2000"}
            },
            "required": ["chat"]
        }
    },
    {
        "name": "search_messages",
        "description": "在最近 N 天消息中按关键词搜索（可限定某个会话）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "关键词"},
                "chat": {"type": "string", "description": "可选，限定会话名称/id"},
                "days": {"type": "integer", "description": "回看天数，默认7，最大30"},
                "limit": {"type": "integer", "description": "最多返回条数，默认200"}
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "status",
        "description": "查看微信数据库连接状态（账号、解锁的数据库数、会话数）。",
        "inputSchema": {"type": "object", "properties": {}}
    },
]

HANDLERS = {
    "list_conversations": tool_list_conversations,
    "get_messages": tool_get_messages,
    "search_messages": tool_search_messages,
    "status": tool_status,
}


def send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(req):
    method = req.get("method")
    rid = req.get("id")
    try:
        if method == "initialize":
            send({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": req.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "wechat-chatlog", "version": "1.0.0"},
            }})
        elif method == "notifications/initialized":
            pass  # 通知，无需回复
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            handler = HANDLERS.get(name)
            if handler is None:
                send({"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": f"未知工具: {name}"}], "isError": True}})
            else:
                result = handler(params.get("arguments") or {})
                send({"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=1)}]}})
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": rid, "result": {}})
        elif rid is not None:
            send({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"未知方法: {method}"}})
    except Exception:
        err = traceback.format_exc()
        sys.stderr.write(err + "\n")
        if rid is not None:
            send({"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": "工具执行失败:\n" + err[-800:]}], "isError": True}})


def main():
    sys.stderr.write("wechat-chatlog MCP server started\n")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(req, dict):
            handle(req)


if __name__ == "__main__":
    main()
