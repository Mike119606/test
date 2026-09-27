import json
import subprocess
import sys
import threading

PY = r"c:\Users\应轩旸\Documents\trae_projects\001\python313\python.exe"
SERVER = r"c:\Users\应轩旸\Documents\trae_projects\001\wechat_mcp_server.py"

proc = subprocess.Popen([PY, "-X", "utf8", SERVER], stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

responses = {}

def reader():
    for line in proc.stdout:
        try:
            obj = json.loads(line)
            responses[obj.get("id")] = obj
        except Exception as e:
            print("BAD LINE:", e)

t = threading.Thread(target=reader, daemon=True)
t.start()

def call(rid, method, params=None, wait=120):
    req = {"jsonrpc": "2.0", "id": rid, "method": method}
    if params is not None:
        req["params"] = params
    proc.stdin.write((json.dumps(req) + "\n").encode("utf-8"))
    proc.stdin.flush()
    deadline = 0
    for _ in range(wait * 10):
        if rid in responses:
            return responses[rid]
        deadline += 0.1
        threading.Event().wait(0.1)
    return {"error": "timeout"}

r = call(1, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                           "clientInfo": {"name": "test", "version": "0"}})
print("INIT:", json.dumps(r.get("result", r), ensure_ascii=False)[:200])

r = call(2, "tools/list")
print("TOOLS:", [t["name"] for t in r["result"]["tools"]])

r = call(3, "tools/call", {"name": "status", "arguments": {}})
print("STATUS:", json.dumps(json.loads(r["result"]["content"][0]["text"]), ensure_ascii=False))

r = call(4, "tools/call", {"name": "list_conversations",
                           "arguments": {"filter": "半糖德比公会"}})
out = json.loads(r["result"]["content"][0]["text"])
print("LIST:", json.dumps(out, ensure_ascii=False)[:400])

r = call(5, "tools/call", {"name": "get_messages",
                           "arguments": {"chat": "半糖德比公会", "days": 1, "limit": 10}})
out = json.loads(r["result"]["content"][0]["text"])
print("GET:", out.get("count"), "msgs; last 3:")
for line in out.get("messages", [])[-3:]:
    print("   ", line[:120])

r = call(6, "tools/call", {"name": "search_messages",
                           "arguments": {"keyword": "320", "chat": "半糖德比公会", "days": 7, "limit": 5}})
out = json.loads(r["result"]["content"][0]["text"])
print("SEARCH:", out.get("count"), "hits; first 3:")
for line in out.get("messages", [])[:3]:
    print("   ", line[:120])

proc.stdin.close()
proc.wait(timeout=10)
print("EXIT:", proc.returncode)
err = proc.stderr.read().decode("utf-8", "replace")
print("STDERR tail:", err[-300:])
