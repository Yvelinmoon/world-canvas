#!/usr/bin/env python3
"""
world-canvas 文件监听 + 开发服务器
用法：python3 ~/.claude/skills/world-canvas/scripts/watch_canvas.py [PORT]
从你的世界目录下运行，需要先通过 world-canvas skill 生成 /tmp/build_canvas_themed.py
"""
import os, sys, time, threading, subprocess, queue
from http.server import HTTPServer, SimpleHTTPRequestHandler

BUILD_SCRIPT   = "/tmp/build_canvas_themed.py"
WATCH_EXTS     = {'.md', '.png', '.jpg', '.jpeg', '.webp'}
POLL_INTERVAL  = 2  # 秒
PORT           = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

_clients      = []
_clients_lock = threading.Lock()


def rebuild():
    print("[canvas] 检测到变化，重新构建...")
    result = subprocess.run(["python3", BUILD_SCRIPT], capture_output=True, text=True)
    if result.returncode != 0:
        print("[canvas] 构建失败:", result.stderr)
        return
    print("[canvas] 构建完成，通知浏览器刷新")
    with _clients_lock:
        for q in list(_clients):
            q.put("rebuild")


def _snapshot(root):
    s = {}
    for dirpath, dirs, files in os.walk(root):
        # 跳过隐藏目录和无关目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', '.venv', 'node_modules')]
        for f in files:
            if os.path.splitext(f)[1].lower() in WATCH_EXTS:
                fp = os.path.join(dirpath, f)
                s[fp] = os.path.getmtime(fp)
    return s


def watch(root):
    prev = _snapshot(root)
    while True:
        time.sleep(POLL_INTERVAL)
        curr = _snapshot(root)
        if curr != prev:
            prev = curr
            rebuild()


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/events':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            q = queue.Queue()
            with _clients_lock:
                _clients.append(q)
            try:
                while True:
                    try:
                        msg = q.get(timeout=25)
                        self.wfile.write(f"data: {msg}\n\n".encode())
                        self.wfile.flush()
                    except queue.Empty:
                        # 发心跳，防止连接超时断开
                        self.wfile.write(b": heartbeat\n\n")
                        self.wfile.flush()
            except Exception:
                with _clients_lock:
                    if q in _clients:
                        _clients.remove(q)
        else:
            super().do_GET()

    def log_message(self, fmt, *args):
        pass  # 屏蔽访问日志


if __name__ == "__main__":
    if not os.path.exists(BUILD_SCRIPT):
        print(f"[canvas] 错误：找不到 {BUILD_SCRIPT}")
        print("[canvas] 请先通过 world-canvas skill 生成主题化构建脚本")
        sys.exit(1)

    root = os.getcwd()
    print(f"[canvas] 监听目录：{root}")

    # 初始构建
    rebuild()

    # 启动文件监听线程
    t = threading.Thread(target=watch, args=(root,), daemon=True)
    t.start()

    # 启动 HTTP 服务器
    server = HTTPServer(("", PORT), Handler)
    url = f"http://localhost:{PORT}/World_Canvas_Board.html"
    print(f"[canvas] 服务已启动：{url}")
    print("[canvas] Ctrl+C 停止")

    import webbrowser
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[canvas] 已停止")
