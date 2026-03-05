import os
import json
import random
import re
import urllib.parse

def scan_assets(root_dir):
    cards = []

    img_assets = {}
    for path, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                name = os.path.splitext(f)[0]
                rel_img = os.path.relpath(os.path.join(path, f), root_dir).replace('\\', '/')
                img_assets[name] = rel_img
                img_assets[f] = rel_img

    for path, _, files in os.walk(root_dir):
        category = os.path.basename(path)
        if category.startswith('.') or category in ['assets', 'scripts', '__pycache__', '.venv']:
            continue

        for f in files:
            file_path = os.path.join(path, f)
            name, ext = os.path.splitext(f)

            if ext.lower() == '.md':
                with open(file_path, 'r', encoding='utf-8') as mf:
                    content = mf.read()

                img_src = ""
                # 1. 匹配本地同名图片
                if name in img_assets:
                    img_src = img_assets[name]
                else:
                    for img_k, img_v in img_assets.items():
                        if img_k in name or name in img_k:
                            img_src = img_v
                            break

                # 2. 本地没有时，从 md 内容中提取第一张外链图片
                if not img_src:
                    external_urls = re.findall(r'!\[.*?\]\((https?://[^\)]+)\)', content)
                    if external_urls:
                        img_src = external_urls[0]

                rel_file_path = os.path.relpath(file_path, root_dir).replace('\\', '/')

                cards.append({
                    "id": f"card_{len(cards)}",
                    "type": "markdown",
                    "title": name,
                    "category": category if category != os.path.basename(root_dir) else "General",
                    "content": content,
                    "img": img_src,
                    "path": rel_file_path
                })

            elif ext.lower() == '.html' and 'canvas' not in f.lower():
                rel_file_path = os.path.relpath(file_path, root_dir).replace('\\', '/')
                cards.append({
                    "id": f"card_{len(cards)}",
                    "type": "html",
                    "title": name,
                    "category": "Virtual Space",
                    "content": "Interactive Web Asset / 虚拟交互空间",
                    "img": img_assets.get("bg", ""),
                    "path": rel_file_path
                })
    return cards

def generate_html(cards):
    for idx, c in enumerate(cards):
        row = idx // 4
        col = idx % 4
        c['x'] = col * 380 + random.randint(-20, 20) + 200
        c['y'] = row * 450 + random.randint(-20, 20) + 200

    cards_json = json.dumps(cards)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>World Canvas Board</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #121212; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; user-select: none; }}
        #canvas-container {{ width: 100vw; height: 100vh; position: relative; overflow: hidden; cursor: grab; background-image: radial-gradient(#333 1px, transparent 1px); background-size: 40px 40px; }}
        #canvas-container:active {{ cursor: grabbing; }}
        #board {{ position: absolute; transform-origin: 0 0; width: 10000px; height: 10000px; }}

        .card {{
            position: absolute;
            width: 320px;
            min-height: 200px;
            background: #1e1e1e;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            border: 1px solid #333;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            cursor: default;
            transition: box-shadow 0.2s, border 0.2s;
            resize: both;
            min-width: 250px;
            max-width: 800px;
            max-height: 800px;
        }}
        .card:hover {{ border-color: #555; box-shadow: 0 12px 32px rgba(0,0,0,0.7); z-index: 100 !important; }}

        .card-header {{ padding: 12px 16px; background: #252525; border-bottom: 1px solid #333; cursor: grab; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }}
        .card-header:active {{ cursor: grabbing; }}
        .card-title {{ margin: 0; font-size: 16px; color: #fff; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .card-category {{ font-size: 11px; padding: 3px 8px; border-radius: 20px; background: #3a3a3a; color: #aaa; flex-shrink: 0; margin-left: 10px; }}

        .card-img-container {{ width: 100%; height: 160px; flex-shrink: 0; border-bottom: 1px solid #333; background: #000; overflow: hidden; display: flex; justify-content: center; align-items: center; }}
        .card-img {{ width: 100%; height: 100%; object-fit: cover; }}

        .card-body {{
            padding: 16px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            overflow-x: hidden;
            background: #1e1e1e;
        }}
        .card-body::-webkit-scrollbar {{ width: 6px; }}
        .card-body::-webkit-scrollbar-track {{ background: #1a1a1a; }}
        .card-body::-webkit-scrollbar-thumb {{ background: #444; border-radius: 3px; }}
        .card-body::-webkit-scrollbar-thumb:hover {{ background: #555; }}

        .markdown-body {{ margin: 0; font-size: 13px; color: #bbb; line-height: 1.6; word-wrap: break-word; }}
        .markdown-body img {{ max-width: 100%; height: auto; border-radius: 6px; margin: 8px 0; border: 1px solid #444; }}
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {{ color: #eee; margin-top: 10px; margin-bottom: 6px; }}
        .markdown-body p {{ margin-top: 0; margin-bottom: 8px; }}
        .markdown-body a {{ color: #4dabf7; text-decoration: none; }}

        .card-footer {{ padding: 10px 16px; background: #1e1e1e; border-top: 1px solid #333; flex-shrink: 0; }}

        .card.type-html {{ border-color: #0088ff; }}
        .card.type-html .card-header {{ background: #002244; }}

        .btn-launch {{ display: block; width: 100%; padding: 8px; background: #0088ff; color: #fff; text-align: center; border-radius: 6px; font-weight: bold; cursor: pointer; border: none; box-sizing: border-box; }}
        .btn-launch:hover {{ background: #00aaff; }}
        .btn-read {{ display: block; width: 100%; padding: 8px; background: #444; color: #fff; text-align: center; border-radius: 6px; font-weight: bold; cursor: pointer; border: none; box-sizing: border-box; }}
        .btn-read:hover {{ background: #555; }}

        #modal-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); z-index: 9999; backdrop-filter: blur(4px); }}
        #modal-content {{ position: absolute; top: 5%; left: 5%; width: 90%; height: 90%; background: #1e1e1e; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; border: 1px solid #444; box-shadow: 0 20px 50px rgba(0,0,0,0.8); }}
        #modal-header {{ padding: 16px 24px; background: #252525; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; flex-shrink: 0; }}
        #modal-title {{ color: #fff; margin: 0; font-size: 20px; }}
        #close-modal {{ background: transparent; border: none; color: #aaa; font-size: 28px; cursor: pointer; line-height: 1; padding: 0 10px; }}
        #close-modal:hover {{ color: #fff; }}

        #iframe-container {{ flex-grow: 1; width: 100%; height: 100%; border: none; background: #000; }}

        #text-container {{
            flex-grow: 1;
            padding: 40px;
            color: #ddd;
            overflow-y: auto !important;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-sizing: border-box;
            background: #1a1a1a;
        }}
        #text-container::-webkit-scrollbar {{ width: 10px; }}
        #text-container::-webkit-scrollbar-track {{ background: #111; }}
        #text-container::-webkit-scrollbar-thumb {{ background: #555; border-radius: 5px; }}
        #text-container::-webkit-scrollbar-thumb:hover {{ background: #777; }}

        #controls {{ position: fixed; bottom: 20px; right: 20px; background: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 8px; display: flex; gap: 8px; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }}
        .ctrl-btn {{ background: #2d2d2d; color: #fff; border: 1px solid #444; width: 36px; height: 36px; border-radius: 4px; cursor: pointer; font-size: 18px; display: flex; justify-content: center; align-items: center; }}
        .ctrl-btn:hover {{ background: #3d3d3d; }}
    </style>
</head>
<body>
    <div id="canvas-container">
        <div id="board"></div>
    </div>

    <div id="controls">
        <button class="ctrl-btn" onclick="zoom(0.1)">+</button>
        <button class="ctrl-btn" onclick="zoom(-0.1)">-</button>
        <button class="ctrl-btn" onclick="resetView()">⌂</button>
    </div>

    <div id="modal-overlay">
        <div id="modal-content">
            <div id="modal-header">
                <h2 id="modal-title">Title</h2>
                <button id="close-modal">&times;</button>
            </div>
            <iframe id="iframe-container" src="about:blank" style="display:none;"></iframe>
            <div id="text-container" style="display:none;"></div>
        </div>
    </div>

    <script>
        const cardsData = {cards_json};
        const board = document.getElementById('board');

        function resolveRelativePath(basePath, relativePath) {{
            if (!relativePath || relativePath.match(/^(http|https|data):/) || relativePath.startsWith('/')) return relativePath;
            let base = basePath.split('/').slice(0, -1).join('/');
            return base ? base + '/' + relativePath : relativePath;
        }}

        let maxZIndex = 10;
        cardsData.forEach(c => {{
            const el = document.createElement('div');
            el.className = `card type-${{c.type}}`;
            el.style.left = c.x + 'px';
            el.style.top = c.y + 'px';
            el.style.height = c.type === 'html' ? '220px' : '380px';
            el.style.zIndex = maxZIndex;
            el.dataset.id = c.id;

            let imgHtml = '';
            if (c.img) {{
                // 外链图片直接使用，本地图片 encodeURI
                const imgSrc = c.img.match(/^https?:\/\//) ? c.img : encodeURI(c.img);
                imgHtml = `<div class="card-img-container"><img src="${{imgSrc}}" class="card-img" draggable="false" /></div>`;
            }}

            let parsedContent = c.content;
            if (c.type === 'markdown') {{
                parsedContent = marked.parse(c.content);
            }}
            let bodyContent = `<div class="markdown-body">${{parsedContent}}</div>`;

            let footerHtml = '';
            if (c.type === 'html') {{
                footerHtml = `<button class="btn-launch" onclick="openModal('${{c.id}}')">🚀 Launch Space</button>`;
            }} else {{
                footerHtml = `<button class="btn-read" onclick="openModal('${{c.id}}')">📖 Expand Focus View</button>`;
            }}

            el.innerHTML = `
                <div class="card-header" onmousedown="bringToFront(this.parentElement)">
                    <h3 class="card-title">${{c.title}}</h3>
                    <span class="card-category">${{c.category}}</span>
                </div>
                ${{imgHtml}}
                <div class="card-body" onwheel="handleCardScroll(event)">
                    ${{bodyContent}}
                </div>
                <div class="card-footer">
                    ${{footerHtml}}
                </div>
            `;

            const seenImageUrls = new Set();
            if (c.img) {{
                const resolvedImg = c.img.match(/^https?:\/\//) ? c.img : encodeURI(c.img);
                seenImageUrls.add(resolvedImg);
            }}

            el.querySelectorAll('.markdown-body img').forEach(img => {{
                const rawSrc = img.getAttribute('src');
                img.src = rawSrc.match(/^https?:\/\//) ? rawSrc : resolveRelativePath(c.path, rawSrc);
                if (seenImageUrls.has(img.src)) {{
                    const parent = img.parentElement;
                    img.remove();
                    if (parent && parent.tagName === 'P' && parent.innerHTML.trim() === '') {{
                        parent.remove();
                    }}
                }} else {{
                    seenImageUrls.add(img.src);
                }}
            }});

            board.appendChild(el);

            const header = el.querySelector('.card-header');
            let isDraggingCard = false;
            header.addEventListener('mousedown', e => {{
                e.stopPropagation();
                isDraggingCard = true;
                let startX = e.clientX, startY = e.clientY;
                let elStartX = parseFloat(el.style.left), elStartY = parseFloat(el.style.top);

                const onMove = e => {{
                    if(!isDraggingCard) return;
                    el.style.left = (elStartX + (e.clientX - startX)/scale) + 'px';
                    el.style.top = (elStartY + (e.clientY - startY)/scale) + 'px';
                }};
                const onUp = () => {{ isDraggingCard = false; document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp); }};

                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            }});

            el.querySelector('.card-body').addEventListener('mousedown', e => {{
                bringToFront(el);
                e.stopPropagation();
            }});

            el.addEventListener('mousedown', e => {{
                bringToFront(el);
                const rect = el.getBoundingClientRect();
                if (e.clientX > rect.right - 20 && e.clientY > rect.bottom - 20) {{
                    e.stopPropagation();
                }}
            }});
        }});

        window.handleCardScroll = (e) => {{ e.stopPropagation(); }};
        window.bringToFront = (el) => {{ maxZIndex++; el.style.zIndex = maxZIndex; }};

        const overlay = document.getElementById('modal-overlay');
        const mTitle = document.getElementById('modal-title');
        const mIframe = document.getElementById('iframe-container');
        const mText = document.getElementById('text-container');

        mText.addEventListener('wheel', e => e.stopPropagation());

        window.openModal = (id) => {{
            const data = cardsData.find(c => c.id === id);
            mTitle.innerText = data.title;
            overlay.style.display = 'block';

            if (data.type === 'html') {{
                mIframe.src = encodeURI(data.path);
                mIframe.style.display = 'block';
                mText.style.display = 'none';
            }} else {{
                mText.innerHTML = '';
                let modalSeenImages = new Set();

                if (data.img) {{
                    let imgContainer = document.createElement('div');
                    imgContainer.style.cssText = 'width:100%;text-align:center;margin-bottom:40px;';
                    let imgEl = document.createElement('img');
                    imgEl.src = data.img.match(/^https?:\/\//) ? data.img : encodeURI(data.img);
                    imgEl.style.cssText = 'max-width:100%;max-height:60vh;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.8);border:1px solid #444;object-fit:contain;';
                    imgContainer.appendChild(imgEl);
                    mText.appendChild(imgContainer);
                    modalSeenImages.add(imgEl.src);
                }}

                let textDiv = document.createElement('div');
                textDiv.style.cssText = 'width:100%;max-width:900px;font-size:16px;padding-bottom:60px;';
                textDiv.className = 'markdown-body';
                textDiv.innerHTML = data.type === 'markdown' ? marked.parse(data.content) : data.content;

                textDiv.querySelectorAll('img').forEach(img => {{
                    const rawSrc = img.getAttribute('src');
                    img.src = rawSrc.match(/^https?:\/\//) ? rawSrc : resolveRelativePath(data.path, rawSrc);
                    if (modalSeenImages.has(img.src)) {{
                        const parent = img.parentElement;
                        img.remove();
                        if (parent && parent.tagName === 'P' && parent.innerHTML.trim() === '') parent.remove();
                    }} else {{
                        modalSeenImages.add(img.src);
                    }}
                }});

                mText.appendChild(textDiv);
                mText.style.display = 'flex';
                mIframe.style.display = 'none';
                mText.scrollTop = 0;
            }}
        }};

        document.getElementById('close-modal').onclick = () => {{ overlay.style.display = 'none'; mIframe.src = 'about:blank'; }};
        overlay.addEventListener('click', (e) => {{ if (e.target === overlay) {{ overlay.style.display = 'none'; mIframe.src = 'about:blank'; }} }});

        let scale = 1, panning = false, pointX = 0, pointY = 0, start = {{x: 0, y: 0}};
        const container = document.getElementById('canvas-container');

        container.onmousedown = function(e) {{ if (e.target.closest('.card')) return; e.preventDefault(); start = {{x: e.clientX - pointX, y: e.clientY - pointY}}; panning = true; }};
        container.onmouseup = function() {{ panning = false; }};
        container.onmouseleave = function() {{ panning = false; }};
        container.onmousemove = function(e) {{ if (!panning) return; e.preventDefault(); pointX = e.clientX - start.x; pointY = e.clientY - start.y; updateTransform(); }};
        container.onwheel = function(e) {{
            e.preventDefault();
            let xs = (e.clientX - pointX) / scale, ys = (e.clientY - pointY) / scale;
            let delta = e.wheelDelta ? e.wheelDelta : -e.deltaY;
            delta > 0 ? (scale *= 1.1) : (scale /= 1.1);
            scale = Math.min(Math.max(0.15, scale), 3);
            pointX = e.clientX - xs * scale;
            pointY = e.clientY - ys * scale;
            updateTransform();
        }};

        function updateTransform() {{ board.style.transform = `translate(${{pointX}}px, ${{pointY}}px) scale(${{scale}})`; }}
        window.zoom = (dir) => {{ let cx = window.innerWidth/2, cy = window.innerHeight/2, xs = (cx-pointX)/scale, ys = (cy-pointY)/scale; scale = Math.min(Math.max(0.15, scale+dir), 3); pointX = cx-xs*scale; pointY = cy-ys*scale; updateTransform(); }};
        window.resetView = () => {{ scale=1; pointX=0; pointY=0; updateTransform(); }};
        updateTransform();
    </script>
</body>
</html>
"""
    with open("World_Canvas_Board.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    current_dir = os.getcwd()
    assets_data = scan_assets(current_dir)
    generate_html(assets_data)
    print(f"Canvas generated: World_Canvas_Board.html ({len(assets_data)} cards)")
