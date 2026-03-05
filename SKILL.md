---
name: world-canvas
description: 自动遍历当前目录下的世界观设定和媒体资产，并生成一个类似 Figma、Miro 的 2D 无限拖拽与缩放画布页面 (Canvas Board)。自动根据世界观风格生成个性化视觉主题。
---

# 资产画布生成器 (World Canvas)

## 技能描述
你是一个专业的”资产视觉化架构师”。当用户需要总览他们的世界观设定或项目文件时，你要调用此技能，遍历当前工作目录下的所有世界观资产（`.md` 文档、`.png/.jpg` 图片、`.html` 虚拟空间），并自动生成一个类似 Figma、Miro 或 Canva 的 **2D无限拖拽与缩放画布页面 (Canvas Board)**。

**每个世界都有专属主题**：画布会自动读取世界观设定，推断出与世界气质完全匹配的个性化视觉方案——配色、字体、背景图案、卡片风格全部动态生成，不会出现两个相同风格的画布。

## 核心职责

1. **读取目录资产**：
   - 使用 Python 脚本遍历当前目录及所有子目录。
   - 提取出所有 Markdown 文件的标题、内容、以及对应的分类。
   - 提取并匹配所有同名的图片资产（立绘、地图等），准备将它们嵌在卡片顶部。

2. **智能主题推断（执行脚本前必须完成）**：
   - 先读取 `assets/visual_style.md`（如存在）以及世界概述文件
   - 根据世界的风格、时代、氛围，由 Claude 推断出一套完整的视觉主题配置
   - 将推断结果以 `THEME` 字典的形式**硬编码**到 Python 脚本中，不由脚本自行解析文件

3. **生成交互式 HTML 画布**：
   - 在当前项目目录下生成 `build_canvas.py` 并运行，最终生成一个单文件 HTML：`World_Canvas_Board.html`。
   - 画布需具备以下特性：
     - **无限平移与缩放 (Pan & Zoom)**。
     - **可变卡片化设计**：卡片支持**内部滚动条**（不会触发外部缩放），并且卡片右下角可以通过拖拽进行**自由缩放 (Resize)**。
     - **极佳的阅读体验**：点击卡片底部的按钮会弹出 Focus View (全屏模态框)，支持显示高清大图和完整文本，且模态框内的滚动非常丝滑。
     - **世界观主题**：整个画布的配色、字体、背景图案与世界风格高度匹配。

---

## 主题推断规则（必读，每次生成前执行）

### 第一步：读取世界设定

按优先级读取以下文件：
1. `assets/visual_style.md` ← 最高优先级，包含明确的视觉风格说明
2. `lore/world_overview/*.md` ← 世界概述，理解世界气质
3. 其他 `lore/` 文件 ← 补充背景

### 第二步：世界类型判断与主题映射

根据读取内容判断世界类型，选择对应主题基础值，再根据世界细节**微调**（不要照搬，要有个性）：

| 世界类型 | 背景色 | 主强调色 | 背景图案 | 字体方向 |
|---|---|---|---|---|
| 古代·中国历史 | `#0d0c08` | 金 `#c8a84a` | dots-warm | 宋体/衬线 |
| 古代·欧洲中世纪 | `#080b0e` | 暗金 `#a07830` | stone-grid | 衬线 |
| 赛博朋克·科幻 | `#050a12` | 青 `#00d4ff` | grid-neon | 等宽 |
| 奇幻·魔法 | `#07050f` | 紫 `#9b59b6` | stars | 衬线 |
| 末世·废土 | `#0d0905` | 锈橙 `#c0390b` | noise | 粗无衬线 |
| 海洋·蔚蓝 | `#030e1a` | 蓝绿 `#1abc9c` | waves | 无衬线 |
| 蒸汽朋克 | `#0e0a04` | 铜 `#b87333` | dots-warm | 衬线 |
| 现代都市·悬疑 | `#0e0e0e` | 冷白 `#d0d0d0` | grid-clean | 无衬线 |
| 东方·水墨 | `#080d06` | 朱砂 `#c03020` | ink-dots | 楷体/衬线 |
| 宇宙·星际 | `#020408` | 星蓝 `#4a90d9` | stars | 无衬线 |
| 克苏鲁·诡异 | `#050508` | 深绿 `#2ecc71` | noise | 衬线 |

**重要**：主题颜色不要机械照搬表格，应结合世界具体氛围微调色相和明度，让每个世界都是独一无二的。

### 第三步：生成 THEME 字典

在 Python 脚本顶部定义如下 `THEME` 字典，所有字段必须填写：

```python
THEME = {
    # 世界身份
    “world_name”: “世界名称”,
    “world_subtitle”: “副标题/标语”,

    # 字体（使用 Google Fonts，选与世界气质匹配的）
    # 古风选 Noto Serif SC；科幻选 Share Tech Mono 或 Orbitron；
    # 奇幻选 Cinzel；现代选 Inter 或 DM Sans
    “font_url”: “https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&display=swap”,
    “font_family”: “'Noto Serif SC', serif”,

    # 画布背景
    “bg_color”: “#0d0c08”,
    “bg_pattern”: “dots-warm”,  # 见下方图案列表
    “bg_pattern_color”: “#1e1a0e”,
    “bg_pattern_size”: “36px 36px”,

    # 卡片
    “card_bg”: “#161410”,
    “card_border”: “#2e2a18”,
    “card_hover_shadow”: “0 12px 40px rgba(200,168,74,0.2)”,
    “card_hover_border”: “#8B6914”,
    “card_header_bg”: “#1e1a0a”,

    # 文字
    “text_title”: “#e8d09a”,     # 卡片标题
    “text_body”: “#999”,          # 正文
    “text_muted”: “#555”,         # 次要信息

    # 强调色（用于徽章、按钮、高亮）
    “accent”: “#c8a84a”,
    “accent_dim”: “#8B6914”,
    “accent_glow”: “rgba(200,168,74,0.18)”,

    # Banner（顶部标题栏）
    “banner_bg”: “linear-gradient(135deg, #16120a, #1e180a)”,
    “banner_border”: “#6a4e10”,
    “banner_title”: “#e8c97a”,
    “banner_shadow”: “rgba(120,90,20,0.35)”,

    # 模态框
    “modal_bg”: “#0e0d08”,
    “modal_header_bg”: “linear-gradient(135deg, #16120a, #1e180a)”,
    “modal_border”: “#6a4e10”,

    # 按钮
    “btn_bg”: “linear-gradient(135deg, #2e2410, #3c3018)”,
    “btn_color”: “#e0c060”,
    “btn_border”: “#5a4428”,
    “btn_hover_bg”: “linear-gradient(135deg, #4a3c1c, #5a4a28)”,

    # 滚动条
    “scrollbar_thumb”: “#3c2e12”,
    “scrollbar_thumb_hover”: “#6a4e10”,
}
```

### 背景图案 CSS 对照表

在生成 HTML 时，根据 `THEME[“bg_pattern”]` 值选择对应 CSS：

| bg_pattern | CSS background-image |
|---|---|
| `dots-warm` | `radial-gradient({color} 1px, transparent 1px)` |
| `grid-neon` | `linear-gradient({color} 1px, transparent 1px), linear-gradient(90deg, {color} 1px, transparent 1px)` |
| `grid-clean` | `linear-gradient({color} 1px, transparent 1px), linear-gradient(90deg, {color} 1px, transparent 1px)` |
| `stars` | `radial-gradient(ellipse, {color} 1px, transparent 1px), radial-gradient(ellipse, {color} 0.5px, transparent 0.5px)` 双层错位 |
| `waves` | `repeating-linear-gradient(45deg, {color} 0, {color} 1px, transparent 0, transparent 50%)` |
| `ink-dots` | `radial-gradient(ellipse 2px 1px, {color} 0%, transparent 100%)` |
| `noise` | `repeating-linear-gradient(0deg, {color} 0, {color} 1px, transparent 0, transparent 4px), repeating-linear-gradient(90deg, {color} 0, {color} 1px, transparent 0, transparent 8px)` |
| `stone-grid` | `linear-gradient({color} 2px, transparent 2px), linear-gradient(90deg, {color} 2px, transparent 2px)` 较粗 |

---

## 执行方式

当用户触发本技能时，你**必须**按以下顺序执行：

1. 先读取世界设定文件，推断主题（见上方规则）
2. 读取 `scripts/build_canvas.py`（位于本 skill 目录），将脚本顶部的默认 `THEME` 字典**替换**为推断好的定制主题
3. 将修改后的脚本写入 `/tmp/build_canvas_themed.py`，然后在用户的世界目录中运行：

```bash
python3 /tmp/build_canvas_themed.py
```

脚本以 `os.getcwd()` 为扫描根目录，在该目录下输出 `World_Canvas_Board.html`。

> 完整脚本模板见：`scripts/build_canvas.py`（顶部 THEME 字典为默认占位值，每次必须替换）
