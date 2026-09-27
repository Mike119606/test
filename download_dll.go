package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

func main() {
	// 尝试所有可用版本的 DLL，从最新到最旧
	// 通用版可能已删除，使用特定版本
	dlls := []struct {
		name   string
		url    string
		sha256 string
		size   int64
	}{
		{"wx_key.dll", "https://github.com/ycccccccy/wx_key/releases/download/dlls/wx_key.dll", "08d26806e4f9d458abab5d52bab6ba3c2fbaeee466f92c648a614ccc13cc3ba4", 60928},
		{"wx_key-4.1.4.11.dll", "https://github.com/ycccccccy/wx_key/releases/download/dlls/wx_key-4.1.4.11.dll", "7ff5502f267214ea35bbff3e5b5b463be2abc79c9c4f9b00cd55be03c9bbfa43", 41472},
		{"wx_key-4.1.4.10.dll", "https://github.com/ycccccccy/wx_key/releases/download/dlls/wx_key-4.1.4.10.dll", "467529f58d9855a15f54f56af61875f4d30c4efa8e808aeb61241432773fcc5c", 41472},
		{"wx_key-4.1.2.18.dll", "https://github.com/ycccccccy/wx_key/releases/download/dlls/wx_key-4.1.2.18.dll", "d8d5f2c7d5c1aff5cbfc50dd6fde3e36842cb467d30a7f93b50253ce9560fce8", 41472},
	}

	mirrors := []string{
		"",
		"https://ghproxy.net/",
		"https://gh-proxy.com/",
		"https://github.moeyy.xyz/",
		"https://hub.gitmirror.com/",
		"https://gh.h233.eu.org/",
	}

	var lastErr error
	for _, dll := range dlls {
		fmt.Printf("\n=== 尝试下载 %s (期望 %d bytes) ===\n", dll.name, dll.size)
		for j, mirror := range mirrors {
			var url string
			if mirror == "" {
				url = dll.url
			} else {
				url = mirror + dll.url
			}
			fmt.Printf("[%s] 镜像 %d: %s\n", dll.name, j+1, mirror)

			client := &http.Client{
				Timeout: 120 * time.Second,
				CheckRedirect: func(req *http.Request, via []*http.Request) error {
					return nil
				},
			}
			resp, err := client.Get(url)
			if err != nil {
				fmt.Printf("  请求失败: %v\n", err)
				lastErr = err
				continue
			}

			if resp.StatusCode != 200 {
				fmt.Printf("  HTTP %d\n", resp.StatusCode)
				resp.Body.Close()
				lastErr = fmt.Errorf("HTTP %d", resp.StatusCode)
				continue
			}

			dest := "wx_key.dll" // 统一保存为 wx_key.dll
			out, err := os.Create(dest)
			if err != nil {
				fmt.Printf("  创建文件失败: %v\n", err)
				resp.Body.Close()
				lastErr = err
				continue
			}

			n, err := io.Copy(out, resp.Body)
			out.Close()
			resp.Body.Close()

			if err != nil {
				fmt.Printf("  下载失败: %v\n", err)
				os.Remove(dest)
				lastErr = err
				continue
			}

			if n < 1000 {
				fmt.Printf("  文件太小: %d bytes\n", n)
				os.Remove(dest)
				lastErr = fmt.Errorf("file too small")
				continue
			}

			data, _ := os.ReadFile(dest)
			hash := sha256.Sum256(data)
			hashStr := hex.EncodeToString(hash[:])
			fmt.Printf("  下载成功: %d bytes\n", n)
			fmt.Printf("  实际 SHA256: %s\n", hashStr)
			fmt.Printf("  期望 SHA256: %s\n", dll.sha256)
			if hashStr == dll.sha256 {
				fmt.Printf("  SHA256 验证通过!\n")
			} else {
				fmt.Printf("  SHA256 不匹配，但文件已保存\n")
			}
			fmt.Printf("\n成功下载 %s，保存为 wx_key.dll\n", dll.name)
			return
		}
	}

	fmt.Printf("\n所有下载尝试失败，最后错误: %v\n", lastErr)
	os.Exit(1)
}
