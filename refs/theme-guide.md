# 主题配置参考

## 世界类型映射表

根据世界设定选择基础值，再根据细节**微调**（不要机械照搬，要有个性）：

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

---

## THEME 字典字段说明

```python
THEME = {
    # 世界身份
    "world_name": "世界名称",
    "world_subtitle": "副标题/标语",

    # 字体（使用 Google Fonts）
    # 古风选 Noto Serif SC；科幻选 Share Tech Mono 或 Orbitron；
    # 奇幻选 Cinzel；现代选 Inter 或 DM Sans
    "font_url": "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&display=swap",
    "font_family": "'Noto Serif SC', serif",

    # 画布背景
    "bg_color": "#0d0c08",
    "bg_pattern": "dots-warm",  # 见下方图案列表
    "bg_pattern_color": "#1e1a0e",
    "bg_pattern_size": "36px 36px",

    # 卡片
    "card_bg": "#161410",
    "card_border": "#2e2a18",
    "card_hover_shadow": "0 12px 40px rgba(200,168,74,0.2)",
    "card_hover_border": "#8B6914",
    "card_header_bg": "#1e1a0a",

    # 文字
    "text_title": "#e8d09a",
    "text_body": "#999",
    "text_muted": "#555",

    # 强调色
    "accent": "#c8a84a",
    "accent_dim": "#8B6914",
    "accent_glow": "rgba(200,168,74,0.18)",

    # Banner（顶部标题栏）
    "banner_bg": "linear-gradient(135deg, #16120a, #1e180a)",
    "banner_border": "#6a4e10",
    "banner_title": "#e8c97a",
    "banner_shadow": "rgba(120,90,20,0.35)",

    # 模态框
    "modal_bg": "#0e0d08",
    "modal_header_bg": "linear-gradient(135deg, #16120a, #1e180a)",
    "modal_border": "#6a4e10",

    # 按钮
    "btn_bg": "linear-gradient(135deg, #2e2410, #3c3018)",
    "btn_color": "#e0c060",
    "btn_border": "#5a4428",
    "btn_hover_bg": "linear-gradient(135deg, #4a3c1c, #5a4a28)",

    # 滚动条
    "scrollbar_thumb": "#3c2e12",
    "scrollbar_thumb_hover": "#6a4e10",
}
```

---

## 背景图案 CSS 对照表

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
