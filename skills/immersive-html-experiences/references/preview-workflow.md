# 浏览器预览工作流（Hermes CDP）

使用电脑自带的 CDP 浏览器预览 HTML 页面，验证视觉效果。

## 标准流程

```bash
# 1. 启动 HTTP 服务器（background）
cd ~/Desktop/hermes/[项目目录]
python3 -m http.server 8899 --bind 0.0.0.0
# → 使用 terminal(background=true) 启动

# 2. 浏览器打开
browser_navigate(http://43.138.221.174:8899)
# 或 localhost:8899（如果CDP无法路由公网IP）

# 3. 修改代码后刷新
# kill 旧 server → 启动新 server → 用 ?t=N 参数打开
kill $(lsof -ti:8899) 2>/dev/null
python3 -m http.server 8899 --bind 0.0.0.0
browser_navigate(http://43.138.221.174:8899/?t=1)
# t值每次递增，避免CDP缓存

# 4. 验证
browser_vision(question="描述页面视觉效果")
```

## 注意

- CDP 浏览器会缓存页面。`?t=N` 参数是强制刷新手段
- 旧 server 可能 hold 住端口。先 `lsof -i:8899` 检查，再 kill
- 用 `terminal(background=true)` 启动 server，不要用 `&` 在 foreground
- 文件存 `~/Desktop/hermes/[项目名]/index.html`
