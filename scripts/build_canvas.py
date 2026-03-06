import os, json, random, re

# ============================================================
# THEME — Claude 根据世界观推断后注入，每次调用必须定制
# ============================================================
THEME = {
    "world_name": "World Canvas",
    "world_subtitle": "世界观档案画布",
    "font_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
    "font_family": "'Inter', sans-serif",
    "bg_color": "#0e0e0e",
    "bg_pattern": "dots-warm",
    "bg_pattern_color": "#222",
    "bg_pattern_size": "36px 36px",
    "card_bg": "#1a1a1a",
    "card_border": "#2a2a2a",
    "card_hover_border": "#555",
    "card_hover_shadow": "0 12px 36px rgba(0,0,0,0.6)",
    "card_header_bg": "#222",
    "text_title": "#eee",
    "text_body": "#999",
    "text_muted": "#555",
    "accent": "#888",
    "accent_dim": "#555",
    "accent_glow": "rgba(150,150,150,0.12)",
    "banner_bg": "linear-gradient(135deg, #1a1a1a, #222)",
    "banner_border": "#444",
    "banner_title": "#eee",
    "banner_shadow": "rgba(0,0,0,0.4)",
    "modal_bg": "#111",
    "modal_header_bg": "linear-gradient(135deg, #1a1a1a, #222)",
    "modal_border": "#444",
    "btn_bg": "linear-gradient(135deg, #2a2a2a, #333)",
    "btn_color": "#ccc",
    "btn_border": "#444",
    "btn_hover_bg": "linear-gradient(135deg, #333, #444)",
    "scrollbar_thumb": "#333",
    "scrollbar_thumb_hover": "#555",
}


def get_bg_pattern_css(pattern, color, size):
    patterns = {
        "dots-warm":  f"radial-gradient({color} 1px, transparent 1px)",
        "grid-neon":  f"linear-gradient({color} 1px, transparent 1px), linear-gradient(90deg, {color} 1px, transparent 1px)",
        "grid-clean": f"linear-gradient({color} 1px, transparent 1px), linear-gradient(90deg, {color} 1px, transparent 1px)",
        "stars":      f"radial-gradient(ellipse, {color} 1px, transparent 1px), radial-gradient(ellipse, {color} 0.5px, transparent 0.5px)",
        "waves":      f"repeating-linear-gradient(45deg, {color} 0, {color} 1px, transparent 0, transparent 50%)",
        "ink-dots":   f"radial-gradient(ellipse 2px 1px, {color} 0%, transparent 100%)",
        "noise":      f"repeating-linear-gradient(0deg, {color} 0, {color} 1px, transparent 0, transparent 4px), repeating-linear-gradient(90deg, {color} 0, {color} 1px, transparent 0, transparent 8px)",
        "stone-grid": f"linear-gradient({color} 2px, transparent 2px), linear-gradient(90deg, {color} 2px, transparent 2px)",
    }
    return patterns.get(pattern, patterns["dots-warm"])


def scan_assets(root_dir):
    cards = []
    img_assets = {}

    for path, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                name = os.path.splitext(f)[0]
                rel = os.path.relpath(os.path.join(path, f), root_dir).replace('\\', '/')
                img_assets[name] = rel
                img_assets[f] = rel

    for path, _, files in os.walk(root_dir):
        category = os.path.basename(path)
        if category.startswith('.') or category in ['assets', 'scripts', '__pycache__', '.venv']:
            continue
        for f in sorted(files):
            fp = os.path.join(path, f)
            name, ext = os.path.splitext(f)

            if ext.lower() == '.md':
                with open(fp, encoding='utf-8') as mf:
                    content = mf.read()
                img_src = ""
                if name in img_assets:
                    img_src = img_assets[name]
                else:
                    for k, v in img_assets.items():
                        if k in name or name in k:
                            img_src = v; break
                if not img_src:
                    m = re.search(r'!\[.*?\]\(([^)]+)\)', content)
                    if m:
                        img_ref = m.group(1)
                        if img_ref.startswith('http'):
                            img_src = img_ref
                        else:
                            abs_img = os.path.normpath(os.path.join(os.path.dirname(fp), img_ref))
                            if os.path.exists(abs_img):
                                img_src = os.path.relpath(abs_img, root_dir).replace('\\', '/')
                rel_path = os.path.relpath(fp, root_dir).replace('\\', '/')
                cards.append({
                    "id": f"card_{len(cards)}", "type": "markdown",
                    "title": name,
                    "category": category if category != os.path.basename(root_dir) else "General",
                    "content": content, "img": img_src, "path": rel_path
                })

            elif ext.lower() == '.html' and 'canvas' not in f.lower():
                rel_path = os.path.relpath(fp, root_dir).replace('\\', '/')
                cards.append({
                    "id": f"card_{len(cards)}", "type": "html",
                    "title": name, "category": "Virtual Space",
                    "content": "Interactive Web Asset", "img": img_assets.get("bg", ""), "path": rel_path
                })
    return cards


def assign_positions(cards):
    cols = {}
    for c in cards:
        cols.setdefault(c['category'], []).append(c)
    for ci, (cat, group) in enumerate(cols.items()):
        for ri, c in enumerate(group):
            c['x'] = 200 + ci * 390 + random.randint(-10, 10)
            c['y'] = 160 + ri * 450 + random.randint(-10, 10)


def generate_html(cards, theme=None):
    t = theme or THEME
    assign_positions(cards)
    cards_json = json.dumps(cards, ensure_ascii=False)
    bg_css = get_bg_pattern_css(t["bg_pattern"], t["bg_pattern_color"], t["bg_pattern_size"])
    font_tag = f'<link href="{t["font_url"]}" rel="stylesheet">' if t.get("font_url") else ""

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>{t['world_name']} — World Canvas</title>
{font_tag}
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
*{{box-sizing:border-box}}
body{{margin:0;overflow:hidden;background:{t['bg_color']};font-family:{t['font_family']};user-select:none}}
#cc{{width:100vw;height:100vh;position:relative;overflow:hidden;cursor:grab;
  background-image:{bg_css};background-size:{t['bg_pattern_size']}}}
#cc:active{{cursor:grabbing}}
#board{{position:absolute;transform-origin:0 0;width:12000px;height:8000px}}
.card{{position:absolute;width:340px;height:420px;background:{t['card_bg']};border-radius:14px;
  box-shadow:0 6px 20px rgba(0,0,0,.6);border:1px solid {t['card_border']};cursor:default;
  display:flex;flex-direction:column;overflow:hidden;resize:both;
  min-width:260px;min-height:180px;max-width:900px;max-height:900px;
  transition:border-color .2s,box-shadow .2s}}
.card:hover{{border-color:{t['card_hover_border']};box-shadow:{t['card_hover_shadow']};z-index:200!important}}
.card-header{{padding:11px 15px;background:{t['card_header_bg']};border-bottom:1px solid {t['card_border']};
  cursor:grab;display:flex;justify-content:space-between;align-items:center;flex-shrink:0}}
.card-header:active{{cursor:grabbing}}
.card-title{{margin:0;font-size:14px;color:{t['text_title']};font-weight:700;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.3px}}
.cat-badge{{font-size:10px;padding:2px 8px;border-radius:20px;flex-shrink:0;margin-left:8px;
  font-weight:600;background:{t['accent_glow']};color:{t['accent']};border:1px solid {t['accent_dim']}}}
.img-wrap{{width:100%;flex-shrink:0;overflow:hidden;display:flex;justify-content:center;align-items:center;background:#080808}}
.img-wrap img{{width:100%;height:100%;object-fit:cover}}
.card-body{{padding:13px;flex-grow:1;overflow-y:auto;overflow-x:hidden;background:{t['card_bg']}}}
.card-body::-webkit-scrollbar{{width:4px}}
.card-body::-webkit-scrollbar-thumb{{background:{t['scrollbar_thumb']};border-radius:2px}}
.card-body::-webkit-scrollbar-thumb:hover{{background:{t['scrollbar_thumb_hover']}}}
.md{{font-size:12.5px;color:{t['text_body']};line-height:1.78;word-wrap:break-word}}
.md h1{{color:{t['text_title']};font-size:15px;margin:8px 0 5px;border-bottom:1px solid {t['card_border']};padding-bottom:3px}}
.md h2{{color:{t['accent']};font-size:13px;margin:7px 0 4px}}
.md h3{{color:{t['accent_dim']};font-size:12.5px;margin:6px 0 3px}}
.md p{{margin:0 0 7px}}
.md strong{{color:{t['accent']}}}
.md a{{color:{t['accent']}}}
.md table{{border-collapse:collapse;width:100%;font-size:11.5px}}
.md td,.md th{{border:1px solid {t['card_border']};padding:3px 7px}}
.md th{{background:{t['card_header_bg']};color:{t['accent']}}}
.md ul,.md ol{{padding-left:18px;margin:3px 0}}
.md li{{margin:2px 0}}
.md blockquote{{border-left:3px solid {t['accent_dim']};margin:6px 0;padding:3px 10px;color:{t['text_muted']};background:{t['card_header_bg']}}}
.md hr{{border:none;border-top:1px solid {t['card_border']};margin:8px 0}}
.md code{{background:{t['card_header_bg']};color:{t['accent']};padding:1px 4px;border-radius:3px;font-size:11.5px}}
.md img{{max-width:100%;border-radius:5px;margin:5px 0;border:1px solid {t['card_border']};display:none}}
.card-footer{{padding:9px 13px;background:{t['card_header_bg']};border-top:1px solid {t['card_border']};flex-shrink:0}}
.btn-read{{display:block;width:100%;padding:7px;background:{t['btn_bg']};color:{t['btn_color']};
  text-align:center;border-radius:7px;font-weight:700;cursor:pointer;border:1px solid {t['btn_border']};
  font-size:12px;transition:background .2s;letter-spacing:.3px;font-family:{t['font_family']}}}
.btn-read:hover{{background:{t['btn_hover_bg']}}}
.btn-launch{{display:block;width:100%;padding:7px;background:#0055aa;color:#fff;
  text-align:center;border-radius:7px;font-weight:700;cursor:pointer;border:none;font-size:12px}}
.btn-launch:hover{{background:#0077cc}}
#banner{{position:fixed;top:14px;left:50%;transform:translateX(-50%);
  background:{t['banner_bg']};border:1px solid {t['banner_border']};
  border-radius:10px;padding:9px 28px;z-index:1000;text-align:center;
  box-shadow:0 4px 24px {t['banner_shadow']};pointer-events:none}}
#banner h1{{margin:0;font-size:18px;color:{t['banner_title']};letter-spacing:2px;font-weight:700}}
#banner p{{margin:2px 0 0;font-size:10px;color:{t['text_muted']};letter-spacing:1.5px}}
#overlay{{display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;
  background:rgba(0,0,0,.92);z-index:9999;backdrop-filter:blur(10px)}}
#modal{{position:absolute;top:3.5%;left:3.5%;width:93%;height:93%;background:{t['modal_bg']};
  border-radius:16px;display:flex;flex-direction:column;overflow:hidden;
  border:1px solid {t['modal_border']};box-shadow:0 28px 70px rgba(0,0,0,.98)}}
#mhdr{{padding:15px 28px;background:{t['modal_header_bg']};display:flex;
  justify-content:space-between;align-items:center;border-bottom:1px solid {t['card_border']};flex-shrink:0}}
#mtitle{{color:{t['text_title']};margin:0;font-size:21px;letter-spacing:1px}}
#mbtn{{background:transparent;border:none;color:{t['text_muted']};font-size:32px;cursor:pointer;padding:0 8px;line-height:1}}
#mbtn:hover{{color:{t['text_title']}}}
#mtext{{flex-grow:1;padding:50px 80px;color:{t['text_body']};overflow-y:auto;
  display:flex;flex-direction:column;align-items:center;background:{t['modal_bg']}}}
#mtext::-webkit-scrollbar{{width:8px}}
#mtext::-webkit-scrollbar-thumb{{background:{t['scrollbar_thumb']};border-radius:4px}}
#mtext::-webkit-scrollbar-thumb:hover{{background:{t['scrollbar_thumb_hover']}}}
#mtext .md img{{display:block!important;max-width:100%;border-radius:8px;margin:8px 0;border:1px solid {t['card_border']}}}
#ctrls{{position:fixed;bottom:22px;right:22px;background:{t['card_bg']};
  border:1px solid {t['card_border']};border-radius:9px;padding:7px;display:flex;gap:5px;z-index:1000}}
.cb{{background:{t['card_header_bg']};color:{t['accent']};border:1px solid {t['card_border']};
  width:37px;height:37px;border-radius:6px;cursor:pointer;font-size:17px;
  display:flex;justify-content:center;align-items:center;transition:background .2s}}
.cb:hover{{background:{t['card_border']}}}
#counter{{position:fixed;bottom:22px;left:22px;background:{t['card_bg']};
  border:1px solid {t['card_border']};border-radius:7px;padding:7px 15px;
  color:{t['text_muted']};font-size:11.5px;z-index:1000}}
</style>
</head>
<body>
<div id="cc"><div id="board"></div></div>
<div id="banner"><h1>{t['world_name']}</h1><p>{t['world_subtitle']}</p></div>
<div id="ctrls">
  <button class="cb" onclick="zoom(.15)">＋</button>
  <button class="cb" onclick="zoom(-.15)">－</button>
  <button class="cb" onclick="resetView()">⌂</button>
</div>
<div id="counter"></div>
<div id="overlay">
  <div id="modal">
    <div id="mhdr"><h2 id="mtitle"></h2><button id="mbtn">&times;</button></div>
    <div id="mtext"></div>
  </div>
</div>
<script>
const DATA={cards_json};
const board=document.getElementById('board');
document.getElementById('counter').textContent=`共 ${{DATA.length}} 份档案`;
function resolvePath(base,rel){{
  if(!rel||rel.startsWith('http')||rel.startsWith('data:')||rel.startsWith('/'))return rel;
  const b=base.split('/').slice(0,-1).join('/');
  return b?b+'/'+rel:rel;
}}
let maxZ=20;
DATA.forEach(c=>{{
  const el=document.createElement('div');
  el.className='card type-'+c.type;
  el.style.cssText=`left:${{c.x}}px;top:${{c.y}}px;z-index:${{maxZ++}}`;
  const imgH=c.category==='characters'?'220px':c.img?'160px':'0px';
  const imgSrc=c.img?(c.img.startsWith('http')?c.img:encodeURI(c.img)):'';
  const imgHtml=c.img?`<div class="img-wrap" style="height:${{imgH}}"><img src="${{imgSrc}}" draggable="false" onerror="this.parentElement.style.display='none'"></div>`:'';
  const parsed=marked.parse(c.content);
  const footer=c.type==='html'
    ?`<button class="btn-launch" onclick="openModal('${{c.id}}')">🚀 Launch</button>`
    :`<button class="btn-read" onclick="openModal('${{c.id}}')">📜 展开阅读</button>`;
  el.innerHTML=`
    <div class="card-header">
      <h3 class="card-title">${{c.title}}</h3>
      <span class="cat-badge">${{c.category}}</span>
    </div>
    ${{imgHtml}}
    <div class="card-body" onwheel="event.stopPropagation()">
      <div class="md">${{parsed}}</div>
    </div>
    <div class="card-footer">${{footer}}</div>`;
  el.querySelectorAll('.md img').forEach(i=>{{
    const s=i.getAttribute('src');
    i.src=s.startsWith('http')?s:resolvePath(c.path,s);
  }});
  board.appendChild(el);
  el.querySelector('.card-header').addEventListener('mousedown',e=>{{
    e.stopPropagation();bringToFront(el);
    let sx=e.clientX,sy=e.clientY,ex=parseFloat(el.style.left),ey=parseFloat(el.style.top);
    const mv=e=>{{el.style.left=(ex+(e.clientX-sx)/scale)+'px';el.style.top=(ey+(e.clientY-sy)/scale)+'px'}};
    const up=()=>{{document.removeEventListener('mousemove',mv);document.removeEventListener('mouseup',up)}};
    document.addEventListener('mousemove',mv);document.addEventListener('mouseup',up);
  }});
  el.addEventListener('mousedown',e=>{{bringToFront(el);e.stopPropagation()}});
}});
function bringToFront(el){{el.style.zIndex=++maxZ}}
const overlay=document.getElementById('overlay'),mtext=document.getElementById('mtext');
mtext.addEventListener('wheel',e=>e.stopPropagation());
window.openModal=id=>{{
  const d=DATA.find(c=>c.id===id);
  document.getElementById('mtitle').innerText=d.title;
  mtext.innerHTML='';
  if(d.img){{
    const w=document.createElement('div');
    w.style.cssText='width:100%;text-align:center;margin-bottom:40px';
    const img=document.createElement('img');
    img.src=d.img.startsWith('http')?d.img:encodeURI(d.img);
    img.style.cssText='max-width:100%;max-height:55vh;border-radius:14px;box-shadow:0 10px 50px rgba(0,0,0,.95);object-fit:contain';
    img.onerror=()=>w.style.display='none';
    w.appendChild(img);mtext.appendChild(w);
  }}
  const div=document.createElement('div');
  div.className='md';
  div.style.cssText='width:100%;max-width:860px;font-size:15px;line-height:1.88;padding-bottom:80px';
  const mdContent=d.img?d.content.replace(/!\[.*?\]\([^)]+\)\n?/,''):d.content;
  div.innerHTML=marked.parse(mdContent);
  div.querySelectorAll('img').forEach(i=>{{
    const s=i.getAttribute('src');
    i.src=s.startsWith('http')?s:resolvePath(d.path,s);
    i.style.display='block';
  }});
  mtext.appendChild(div);mtext.style.display='flex';mtext.scrollTop=0;
  overlay.style.display='block';
}};
document.getElementById('mbtn').onclick=()=>overlay.style.display='none';
overlay.addEventListener('click',e=>{{if(e.target===overlay)overlay.style.display='none'}});
let scale=.82,px=0,py=0,sx=0,sy=0,panning=false;
const cc=document.getElementById('cc');
cc.onmousedown=e=>{{if(e.target.closest('.card'))return;e.preventDefault();sx=e.clientX-px;sy=e.clientY-py;panning=true}};
cc.onmouseup=()=>panning=false;cc.onmouseleave=()=>panning=false;
cc.onmousemove=e=>{{if(!panning)return;px=e.clientX-sx;py=e.clientY-sy;upd()}};
cc.onwheel=e=>{{
  e.preventDefault();
  const xs=(e.clientX-px)/scale,ys=(e.clientY-py)/scale;
  const d=e.wheelDelta?e.wheelDelta:-e.deltaY;
  d>0?scale*=1.1:scale/=1.1;scale=Math.min(Math.max(.1,scale),3.5);
  px=e.clientX-xs*scale;py=e.clientY-ys*scale;upd();
}};
function upd(){{board.style.transform=`translate(${{px}}px,${{py}}px) scale(${{scale}})`}}
window.zoom=d=>{{const cx=innerWidth/2,cy=innerHeight/2,xs=(cx-px)/scale,ys=(cy-py)/scale;
  scale=Math.min(Math.max(.1,scale+d),3.5);px=cx-xs*scale;py=cy-ys*scale;upd()}};
window.resetView=()=>{{scale=.82;px=0;py=0;upd()}};
upd();
</script>
</body>
</html>"""

    with open("World_Canvas_Board.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"World_Canvas_Board.html generated ({len(cards)} cards) — {t['world_name']}")


if __name__ == "__main__":
    cards = scan_assets(os.getcwd())
    generate_html(cards, THEME)
