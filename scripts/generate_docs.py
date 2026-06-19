#!/usr/bin/env python3
"""
璧山好房 · 方案讨论文档 → PDF + PPT 生成器
生成排版清爽、配色清新、带目录和思维导图的精美文档
"""

import os
import re
from pathlib import Path

# ============================================================
# 配色方案
# ============================================================
COLORS = {
    "primary": (22, 160, 133),       # #16A085 主色
    "primary_dark": (15, 120, 100),   # 深主色
    "accent": (38, 166, 154),         # #26A69A 强调色
    "warm": (230, 126, 34),           # #E67E22 暖色点缀
    "bg_light": (245, 250, 248),      # 浅绿背景
    "bg_white": (255, 255, 255),
    "text_dark": (44, 62, 80),        # #2C3E50 正文
    "text_gray": (127, 140, 141),     # #7F8C8D 次要文字
    "card_bg": (236, 240, 241),       # 卡片背景
    "line": (189, 195, 199),          # 线条
    "red": (231, 76, 60),
    "green": (39, 174, 96),
    "blue": (41, 128, 185),
    "orange": (243, 156, 18),
    "purple": (142, 68, 173),
}

# ============================================================
# 读取 Markdown 文件
# ============================================================
def read_md(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================
# Chinese text wrapping helper
# ============================================================
def chunk_text(text, max_chars):
    """按中文字符拆分长文本"""
    result = []
    while len(text) > max_chars:
        # 找最近的空格或标点断句
        idx = max_chars
        for sep in "，。；！？、\n ":
            pos = text[:max_chars].rfind(sep)
            if pos > max_chars * 0.6:
                idx = pos + 1
                break
        result.append(text[:idx].strip())
        text = text[idx:].strip()
    if text:
        result.append(text)
    return result


# ============================================================
# PDF 生成 (fpdf2)
# ============================================================
def generate_pdf(md_content, output_path):
    from fpdf import FPDF

    # Find a Chinese-capable font (Windows)
    font_paths = [
        ("C:/Windows/Fonts/msyh.ttc", "Microsoft YaHei"),
        ("C:/Windows/Fonts/msyhbd.ttc", "Microsoft YaHei Bold"),
        ("C:/Windows/Fonts/simsun.ttc", "SimSun"),
        ("C:/Windows/Fonts/simhei.ttf", "SimHei"),
        ("C:/Windows/Fonts/STKAITI.TTF", "STKaiti"),
    ]
    # Find first available font
    font_regular = None
    font_bold = None
    for fp, name in font_paths:
        if os.path.exists(fp):
            if font_regular is None:
                font_regular = fp
            elif "bold" in name.lower() or "bd" in fp.lower() or "hei" in name.lower():
                if font_bold is None:
                    font_bold = fp

    if font_regular is None:
        # Try to find any CJK font
        for root, dirs, files in os.walk("C:/Windows/Fonts"):
            for f in files:
                if f.lower().endswith(('.ttf', '.ttc', '.otf')) and any(
                    kw in f.lower() for kw in ['yahei', 'hei', 'song', 'kai', 'ming']
                ):
                    font_paths.append((os.path.join(root, f), f))
                    break
        raise FileNotFoundError("No Chinese font found. Please install a Chinese font.")

    print(f"Using font: {font_regular}")
    print(f"Using bold font: {font_bold or font_regular}")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Register fonts
    pdf.add_font("CJK", "", font_regular, uni=True)
    if font_bold:
        pdf.add_font("CJKBold", "", font_bold, uni=True)

    def set_font(size=11, bold=False):
        if bold and font_bold:
            pdf.set_font("CJKBold", size=size)
        else:
            pdf.set_font("CJK", size=size)

    # ---- Helper functions ----
    def add_cover():
        """封面"""
        pdf.add_page()
        # Background rectangle
        pdf.set_fill_color(*COLORS["primary"])
        pdf.rect(0, 0, 210, 80, "F")

        # Decorative line
        pdf.set_fill_color(*COLORS["accent"])
        pdf.rect(0, 80, 210, 4, "F")

        # Rest white
        pdf.set_fill_color(*COLORS["bg_light"])
        pdf.rect(0, 84, 210, 213, "F")

        # Title
        pdf.set_y(30)
        pdf.set_text_color(255, 255, 255)
        set_font(28)
        pdf.cell(0, 14, "璧山好房", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        set_font(16)
        pdf.cell(0, 10, "独立经纪人小平 · 个人IP官网", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        set_font(11)
        pdf.cell(0, 8, "方案讨论稿", align="C", new_x="LMARGIN", new_y="NEXT")

        # Central tagline
        pdf.set_y(100)
        pdf.set_text_color(*COLORS["text_dark"])
        set_font(14)
        pdf.cell(0, 10, "个人电子名片 + 可移动智能前台 = 经纪人的个人 IP 官网", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)
        pdf.ln(4)
        pdf.set_text_color(*COLORS["text_gray"])
        set_font(10)
        pdf.cell(0, 8, "一个链接，发到哪都能打开，跨平台汇聚客户", align="C", new_x="LMARGIN", new_y="NEXT")

        # Bottom info
        pdf.set_y(250)
        pdf.set_text_color(*COLORS["text_gray"])
        set_font(9)
        pdf.cell(0, 7, f"项目代号：BishanNest · 璧山好房", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "技术方案：响应式网页 · GitHub Pages · DeepSeek AI", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "成本：0 元启动", align="C", new_x="LMARGIN", new_y="NEXT")

    def add_toc(items):
        """目录页"""
        pdf.add_page()
        pdf.set_fill_color(*COLORS["primary"])
        pdf.rect(0, 0, 210, 3, "F")

        pdf.set_y(20)
        pdf.set_text_color(*COLORS["primary_dark"])
        set_font(22)
        pdf.cell(0, 12, "目  录", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        for title, page_num in items:
            pdf.set_text_color(*COLORS["text_dark"])
            set_font(12)
            # Section number in accent color
            pdf.cell(10, 9, "", new_x="RIGHT", new_y="LAST")
            pdf.set_text_color(*COLORS["text_dark"])
            # Title
            available_w = 170
            pdf.cell(available_w, 9, title, new_x="RIGHT", new_y="LAST")
            # Dots
            pdf.set_text_color(*COLORS["text_gray"])
            set_font(10)
            pdf.cell(0, 9, f"{page_num}", align="R", new_x="LMARGIN", new_y="NEXT")

            # Light separator
            y = pdf.get_y()
            pdf.set_draw_color(*COLORS["line"])
            pdf.set_line_width(0.1)
            pdf.line(15, y, 195, y)
            pdf.ln(3)

    def add_mindmap():
        """思维导图页"""
        pdf.add_page()
        pdf.set_fill_color(*COLORS["primary"])
        pdf.rect(0, 0, 210, 3, "F")

        pdf.set_y(18)
        pdf.set_text_color(*COLORS["primary_dark"])
        set_font(20)
        pdf.cell(0, 12, "项目全景 · 思维导图", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # Center node
        cx, cy = 105, 65
        # Draw center
        pdf.set_fill_color(*COLORS["primary"])
        pdf.set_text_color(255, 255, 255)
        pdf.set_draw_color(*COLORS["primary_dark"])
        pdf.set_line_width(0.8)
        # Use text as center
        pdf.set_y(cy - 4)
        set_font(11)
        pdf.cell(0, 8, "┌─────────────────────┐", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, "│  🏠 璧山好房 · 小平个人IP官网  │", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, "└─────────────────────┘", align="C", new_x="LMARGIN", new_y="NEXT")

        # Branch nodes
        branches = [
            ("🎙️ 语音找房", 30, 110),
            ("🤖 AI数字分身", 30, 130),
            ("📊 地图+详情", 30, 150),
            ("📋 需求卡片", 30, 170),
            ("💬 温暖转化", 30, 190),
            ("🖥️ 经纪人后台", 135, 110),
            ("📱 移动端客户版", 135, 130),
            ("📝 知识库", 135, 150),
            ("🔒 四级分层", 135, 170),
            ("💰 0元部署", 135, 190),
            ("👤 客户", 15, 80),
            ("👩‍💼 小平", 175, 80),
            ("🔗 微信生态", 95, 215),
        ]

        pdf.set_text_color(*COLORS["text_dark"])
        set_font(9)
        for text, bx, by in branches:
            pdf.set_xy(bx, by)
            pdf.set_fill_color(*COLORS["bg_light"])
            pdf.set_draw_color(*COLORS["accent"])
            pdf.set_line_width(0.4)
            rect_w = pdf.get_string_width(text) + 12
            pdf.rect(bx, by, rect_w, 7, "DF")
            pdf.set_xy(bx + 6, by + 1)
            pdf.cell(rect_w - 12, 6, text)

        # Bottom: key differentiators
        pdf.set_y(230)
        pdf.set_text_color(*COLORS["primary_dark"])
        set_font(12)
        pdf.cell(0, 8, "核心定位", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        pdf.set_text_color(*COLORS["text_dark"])
        set_font(10)
        diffs = [
            "贝壳 = 超市（卖信息）  |  小平H5 = 私厨（卖判断）",
            "买房最终是人对人的信任，不是人对平台的搜索",
            "公众号 = 广播站  |  H5 = 智能前台（AI 1v1接待）",
        ]
        for d in diffs:
            pdf.cell(0, 7, d, align="C", new_x="LMARGIN", new_y="NEXT")

    def add_section_title(num, title):
        """添加章节标题"""
        pdf.set_fill_color(*COLORS["primary"])
        pdf.rect(0, 0, 210, 3, "F")
        pdf.ln(12)
        pdf.set_text_color(*COLORS["primary_dark"])
        set_font(18)
        pdf.cell(0, 12, f"{num}  {title}", align="L", new_x="LMARGIN", new_y="NEXT")
        # Underline
        y = pdf.get_y()
        pdf.set_draw_color(*COLORS["accent"])
        pdf.set_line_width(0.6)
        pdf.line(10, y + 1, 100, y + 1)
        pdf.ln(8)

    def add_sub_title(text):
        """添加小节标题"""
        pdf.set_text_color(*COLORS["text_dark"])
        set_font(13, bold=True)
        pdf.cell(0, 9, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    def add_body(text):
        """添加正文"""
        pdf.set_text_color(*COLORS["text_dark"])
        set_font(10)
        lines = chunk_text(text, 80)
        for line in lines:
            pdf.cell(0, 6.5, line, new_x="LMARGIN", new_y="NEXT")

    def add_code_block(text):
        """代码块"""
        pdf.ln(2)
        lines = text.strip().split("\n")
        block_h = len(lines) * 5.5 + 6
        pdf.set_fill_color(44, 62, 80)
        start_y = pdf.get_y()
        pdf.rect(12, start_y, 186, block_h, "F")
        pdf.set_text_color(46, 204, 113)
        set_font(8)
        pdf.set_y(start_y + 3)
        for line in lines:
            pdf.set_x(18)
            pdf.cell(0, 5.5, line[:90], new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*COLORS["text_dark"])
        pdf.ln(4)

    def add_table(headers, rows, col_widths=None):
        """添加表格"""
        pdf.ln(2)
        if col_widths is None:
            col_widths = [180 // len(headers)] * len(headers)

        # Header
        pdf.set_fill_color(*COLORS["primary"])
        pdf.set_text_color(255, 255, 255)
        set_font(9, bold=True)
        start_x = pdf.get_x()
        for i, (h, w) in enumerate(zip(headers, col_widths)):
            pdf.cell(w, 8, h, border=0, fill=True, align="C", new_x="RIGHT", new_y="LAST")
        pdf.ln()

        # Rows
        for row_idx, row in enumerate(rows):
            if row_idx % 2 == 0:
                pdf.set_fill_color(*COLORS["bg_light"])
            else:
                pdf.set_fill_color(*COLORS["bg_white"])

            pdf.set_text_color(*COLORS["text_dark"])
            set_font(9)
            for i, (cell, w) in enumerate(zip(row, col_widths)):
                align = "C" if i > 0 else "L"
                pdf.cell(w, 7, str(cell)[:w * 2], fill=True, align=align, new_x="RIGHT", new_y="LAST")
            pdf.ln()

        pdf.set_text_color(*COLORS["text_dark"])
        pdf.ln(3)

    def add_highlight_box(text, color_key="accent"):
        """高亮信息框"""
        pdf.ln(2)
        pdf.set_fill_color(*COLORS[color_key])
        pdf.set_draw_color(*COLORS[color_key])
        pdf.set_line_width(0.4)
        lines = text.strip().split("\n")
        box_h = max(len(lines) * 7 + 10, 20)
        current_y = pdf.get_y()
        pdf.rect(12, current_y, 186, box_h, "DF")
        pdf.set_text_color(255, 255, 255)
        set_font(10)
        pdf.set_y(current_y + 5)
        for line in lines:
            pdf.set_x(18)
            pdf.cell(0, 7, line[:85], new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*COLORS["text_dark"])
        pdf.ln(5)

    def add_card_box(text, color_key="bg_light"):
        """卡片样式"""
        pdf.ln(2)
        pdf.set_fill_color(*COLORS[color_key])
        pdf.set_draw_color(*COLORS["line"])
        pdf.set_line_width(0.3)
        lines = text.strip().split("\n")
        box_h = max(len(lines) * 7 + 8, 20)
        current_y = pdf.get_y()
        pdf.rect(14, current_y, 182, box_h, "DF")
        pdf.set_text_color(*COLORS["text_dark"])
        set_font(9)
        pdf.set_y(current_y + 4)
        for line in lines:
            pdf.set_x(20)
            pdf.cell(0, 7, line[:82], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # ---- Build PDF ----
    bookmarks = []

    # Cover
    add_cover()

    # TOC placeholder (we'll fill after building content)
    toc_items = [
        ("一、这是什么？", 0),
        ("二、客户使用流程", 0),
        ("三、用户分群策略", 0),
        ("四、为什么这个模式不一样？", 0),
        ("五、主要功能模块", 0),
        ("六、经纪人 IP 生态", 0),
        ("七、推广渠道盘点", 0),
        ("八、待和经纪人讨论的问题", 0),
        ("九、成本", 0),
        ("十、下一步", 0),
    ]

    # Mindmap
    add_mindmap()

    # ---- Section 1: 这是什么 ----
    toc_items[0] = ("一、这是什么？", pdf.page_no())
    pdf.add_page()
    add_section_title("一", "这是什么？")

    add_body("一个响应式网页（手机+电脑自适应），微信里点开就能用，不用下载 App。")
    pdf.ln(2)
    add_highlight_box("个人电子名片 + 可移动智能前台 = 经纪人的个人 IP 官网", "primary")

    # Three pillars
    pdf.ln(2)
    pillars = [
        ("电子名片", "一个链接，发到哪都能打开，展示你的专业度"),
        ("智能前台", "24h × 7天，AI 替你接客，语音+匹配+引导"),
        ("IP 官网", "不是贝壳的分支，是你自己的品牌主页。平台是别人的，但这个链接里的数据和关系是你的。"),
    ]
    for title, desc in pillars:
        pdf.set_fill_color(*COLORS["bg_light"])
        pdf.set_draw_color(*COLORS["accent"])
        y = pdf.get_y()
        pdf.rect(14, y, 182, 12, "DF")
        pdf.set_text_color(*COLORS["primary_dark"])
        set_font(11, bold=True)
        pdf.set_x(18)
        pdf.cell(0, 6, f"▸ {title}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*COLORS["text_dark"])
        set_font(10)
        pdf.set_x(22)
        pdf.cell(0, 6, desc, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    pdf.ln(4)
    add_body("两套界面，一套代码：手机打开是客户版（语音找房），电脑打开是经纪人版（数据管理）。")

    # ---- Section 2: 客户使用流程 ----
    toc_items[1] = ("二、客户使用流程", pdf.page_no())
    pdf.add_page()
    add_section_title("二", "客户使用流程")

    add_code_block("微信分享链接 → 打开页面 → 🎙️说出需求 → AI深度对话\n→ 精选匹配 → 浏览详情 → 📋需求卡片 → 💬温暖转化加微信")

    pdf.ln(2)
    add_sub_title("第一步：语音首页（用户分群入口）")
    add_body("打开页面，中间麦克风按钮。AI 自动识别刚需/改善，语音转文字后 DeepSeek 提取预算、户型、位置、身份、特殊需求，自动打标签进入对应推荐。")
    pdf.ln(1)
    add_body("💡 AI 不是冷冰冰的机器人，是经纪人的数字分身。用经纪人的语调和判断来回复，主动反问了解需求，让用户感觉在跟一个懂行的朋友聊天，而不是在搜贝壳。")

    pdf.ln(3)
    add_sub_title("第二步：AI 深度对话 + 人群精选榜")
    add_body("AI 不直接扔结果，而是像经纪人本人一样先聊几句。聊完之后，根据识别的人群展示精选榜单，每个上榜房源附带：上榜理由（11年经验判断）、适合人群、经纪人备注。")
    pdf.ln(2)
    add_card_box(
        '用户：“璧泉附近有没有三房，60万左右”\n\n❌ 普通AI：“为您匹配以下房源...”\n✅ 小平数字分身：\n  "璧泉60万买三房可以的，我在那边经手过好几套。你主要是自住还是考虑学区？\n   恒大名都性价比高，锦绣新城新一点——要不你先看看这两个？小平对这两个盘特别熟。"'
    )

    pdf.ln(3)
    add_sub_title("🆕 第三步：需求卡片（加微信前的“临门一脚”）")
    add_body("用户浏览过程中，AI 已经在对话和浏览行为中拼出了需求画像。点击加微信前，先弹出需求确认卡片。")
    add_card_box(
        "📋 小平已经帮你整理好了\n\n🏠 类型  刚需首套    💰 预算  60万左右\n🏘️ 户型  三房两厅    📍 区域  璧泉街道\n🎯 关注  交通便利、采光好\n\n✏️ 还想跟小平说：“希望小区安静一点，有老人同住”\n\n💬 发给小平，她已经在看了  →  加微信，小平第一时间回复"
    )
    pdf.ln(2)
    add_body("效果：小平加微信第一句话不是“你好”，而是“王先生，看到你关注璧泉三房，恒大名都刚有一套降价的，要不要先看看？”")

    pdf.ln(3)
    add_sub_title("第四步：楼盘详情 + 信息冰山")
    add_body("展示小区信息、价格走势、经纪人点评、同小区在售概数。底部引导：“榜单只放了几套精选，微信上小平帮你找更合适的。”")

    pdf.ln(3)
    add_sub_title("第五步：微信优先转化（温暖话术）")
    add_body('主按钮：💬 “找小平进一步了解”（唤起微信）')
    add_body('次按钮：📱 “留个电话，小平帮你留意降价”（兜底）')
    pdf.ln(1)
    add_body('⚠️ 全程不用“登录”“注册”“提交”这类冷冰冰的词。每一句引导都像是在介绍一个值得信任的人。')

    # ---- Section 3: 用户分群策略 ----
    toc_items[2] = ("三、用户分群策略", pdf.page_no())
    pdf.add_page()
    add_section_title("三", "用户分群策略：刚需 + 改善双线并行")

    add_sub_title("为什么双线并行？")
    add_table(
        ["", "🏠 刚需", "🏡 改善"],
        [
            ["群体规模", "璧山最大", "稳定增长"],
            ["决策速度", "快（必须买）", "中等（想换但可以等）"],
            ["预算范围", "40-70万", "80-150万"],
            ["核心焦虑", "怕买亏、怕踩坑", "怕换得不够好"],
            ["对中介依赖", "高（什么都不懂）", "中高（需要专业判断）"],
            ["分享意愿", "高（年轻人）", "中（家庭用户）"],
        ],
        [50, 65, 65],
    )

    pdf.ln(2)
    add_body("策略：首页不区分，语音识别后自动分流。两条线共享知识库，但推荐榜单不同。")

    pdf.ln(3)
    add_sub_title("知识库按人群贴标签")
    add_table(
        ["文章", "🏠刚需", "🏡改善"],
        [
            ["璧山买房首付最低多少", "✅", ""],
            ["云巴沿线小区怎么选", "✅", "✅"],
            ["璧山学区房完整盘点", "✅", "✅"],
            ["换房先买还是先卖", "", "✅"],
            ["怎么看翻新装修质量", "✅", "✅"],
            ["秀湖公园板块深度分析", "", "✅"],
        ],
        [80, 40, 40],
    )

    # ---- Section 4: 为什么不一样 ----
    toc_items[3] = ("四、为什么这个模式不一样？", pdf.page_no())
    pdf.add_page()
    add_section_title("四", "为什么这个模式不一样？")

    add_sub_title("H5 vs 朋友圈 vs 贝壳")
    add_table(
        ["", "贝壳/安居客", "朋友圈中介", "你的 H5"],
        [
            ["房源数量", "海量列表", "少量", "精选8套+上榜理由"],
            ["信息深度", "浅", "一言难尽", "经纪人独家判断"],
            ["客户信任", "对平台的", "对人（要熟）", "对人+对专业度"],
            ["获客主动权", "平台分配", "你追客户", "客户找你"],
            ["数据归属", "平台的", "你的微信", "你的"],
            ["24h服务", "有", "没有", "AI替你"],
        ],
        [30, 48, 48, 54],
    )

    pdf.add_page()
    add_sub_title("灵魂拷问：贝壳什么都有，为什么还要做？")
    add_body("贝壳的“全”恰恰是它的弱点。打开贝壳，绿岛新区300套房、20个经纪人可选。你选哪个？答案：随便选一个，或者被平台分配。客户对经纪人的信任是零。")
    pdf.ln(2)
    add_highlight_box("贝壳 = 超市（什么都有，你自己挑）\n你的H5 = 私厨（老板认识你，知道你要什么，帮你挑好了）", "warm")
    pdf.ln(2)
    add_body("在璧山这种熟人社会，私厨比超市有竞争力。")

    pdf.ln(3)
    add_sub_title("贝壳做不到的事")
    add_table(
        ["贝壳能做到", "贝壳永远做不到"],
        [
            ["300套列表，客户选择困难", "8套精选+上榜理由，客户信任你的眼光"],
            ['算法推荐，“猜你喜欢”', '人推荐，"我在璧山卖了11年，这个适合你"'],
            ["20个经纪人竞争同一客户", "只有你一个，客户关系独占"],
            ["客户数据归平台", "数据归你，客户是你的私域资产"],
            ["全中国覆盖，璧山只是几千区县之一", "只做璧山，深度是贝壳的100倍"],
            ["AI 是通用模型", "你的 AI 喂的是你本人的判断"],
            ['“这个房子挂牌75万”', '“这个房子我帮客户谈下来了5万”'],
            ['“本小区均价7200元/㎡”', '“这个楼盘物业最近换了，服务质量下降了”'],
            ["房源信息必须公开透明", '“这个业主急售，底价是XX万，不方便公开写”'],
            ["对串串房保持中立距离", '“这套翻新质量其实不错，我帮你看过”'],
        ],
        [80, 90],
    )

    pdf.ln(3)
    add_highlight_box(
        "贝壳卖的是信息 → 客户自己判断 → 选谁成交都可以\n你卖的是判断 → 客户信任你的眼光 → 只找你成交\n\n贝壳做标准化，你做个性化。贝壳做广度，你做深度。贝壳做平台，你做 IP。\n\n买房最终是人对人的信任，不是人对平台的搜索。",
        "primary",
    )

    pdf.add_page()
    add_sub_title("公众号不也能做吗？")
    add_body("公众号是广播站，H5 是智能前台。角色完全不同。")
    add_code_block("公众号 = 你喊话 → 订阅者听到 → 点开文章 → 看完走了\nH5    = 客户带着需求进来 → AI 1v1接待 → 自己探索 → 加微信")

    pdf.ln(2)
    add_table(
        ["", "公众号", "你的 H5"],
        [
            ["信息方向", "你推给客户（广播）", "客户主动探索（交互）"],
            ["内容形式", "一篇一篇，线性消费", "多入口，非线性探索"],
            ["个性化", "所有人看到一样", "AI根据需求匹配"],
            ["语音交互", "❌ 不支持", "✅ 🎙️ 语音找房"],
            ["用户行为", "只知道阅读量", "知道他在找什么房、预算多少"],
            ["菜单限制", "最多3×5=15个入口", "无限功能入口"],
            ["推送能力", "✅ 模板消息、群发", "❌ 无法主动推送"],
            ["分享传播", "靠文章转发", "链接即用，分享即传播"],
        ],
        [28, 72, 80],
    )

    pdf.ln(2)
    add_body("最关键差异：公众号让你知道“有人看了文章”，H5 让你知道“他在找什么样的家”。")
    pdf.ln(2)
    add_highlight_box(
        "不是替代，是互补\n\n公众号 → 内容吸引 → 关注沉淀 → 推送唤醒 → 推送文末放H5链接\nH5     → 深度交互 → AI匹配 → 行为数据 → 加微信\n\n公众号负责“拉客”，H5负责“接客”。先做H5，因为H5可以独立运行。\n公众号是“放大器”，H5是“发动机”——先有发动机，再配放大器。",
        "accent",
    )

    pdf.add_page()
    add_sub_title("这个产品到底是什么：个人 IP 官网")
    add_highlight_box(
        "个人电子名片 + 可移动智能前台 = 经纪人的个人 IP 官网\n\n· 电子名片：一个链接，发到哪都能打开，展示你的专业度\n· 智能前台：24h × 7天，AI替你接客，语音+匹配+引导\n· IP官网：不是贝壳的分支，是你自己的品牌主页",
        "primary",
    )
    pdf.ln(2)
    add_body("无论客户从哪个平台看到你——朋友圈、微信群、视频号、公众号、小红书、抖音——最终都汇聚到这一个链接。平台是别人的，但这个链接里的数据和关系是你的。")

    pdf.ln(4)
    add_sub_title("一个产品，两端使用")
    add_code_block(
        "一个响应式网页应用\n├── 📱 移动端（客户看）：语音入口 + AI匹配 + 精选榜 + 知识库 + 加微信\n└── 🖥️ 桌面端（经纪人看）：地图管理 + 数据编辑 + 留资查看 + AI助手\n     ↑ 同一套代码，同一份数据，根据屏幕大小自动适配"
    )

    pdf.ln(3)
    add_sub_title("房源展示四级分层")
    add_table(
        ["层级", "内容", "谁可见"],
        [
            ["🟢 公开层", "小区名称、均价、户型、经纪人点评", "所有人"],
            ["🟡 概数层", '"本小区在售约X套"', "所有人"],
            ["🔒 留资层", "完整房源列表、楼层朝向", "加微信/留电话后"],
            ["🔐 微信层", "业主底价、急售、约看时间", "微信1v1"],
        ],
        [30, 90, 50],
    )

    # ---- Section 5: 功能模块 ----
    toc_items[4] = ("五、主要功能模块", pdf.page_no())
    pdf.add_page()
    add_section_title("五", "主要功能模块")

    add_table(
        ["模块", "说明", "对客户的价值"],
        [
            ["🎙️ 语音找房", "说话就能搜房", "不用打字，开口就找"],
            ["🤖 AI数字分身", "用小平的语调和判断对话", "像跟懂行的朋友聊天"],
            ["🗺️ 地图看房", "璧山板块色块+楼盘标注", "快速了解璧山，知道房子在哪"],
            ["📊 楼盘详情", "均价、走势、配套、经纪⼈点评", "全面了解小区"],
            ["📋 需求卡片", "加微信前自动汇总需求画像", "小平第一句话就精准"],
            ["📝 看房知识库", "板块分析、验房技巧、选房攻略", "学到买房知识，信任经纪人"],
            ["💬 温暖转化", '不说“登录注册”', "自然、温暖、不尴尬"],
        ],
        [32, 72, 72],
    )

    # ---- Section 6: 经纪人 IP 生态 ----
    toc_items[5] = ("六、经纪人 IP 生态", pdf.page_no())
    pdf.add_page()
    add_section_title("六", "经纪人 IP 生态")

    add_sub_title("不只是工具，是品牌")
    add_body("H5 不是替代朋友圈，而是给朋友圈装上一个 24小时运转的发动机。")
    add_code_block(
        "普通中介：发朋友圈 → 刷存在感 → 客户被动看到\n小平模式：H5（AI搜索+精选榜+知识库）→ 客户主动探索 → 加微信时已信任"
    )

    pdf.ln(3)
    add_sub_title("精选上榜 = 把经验变成产品")
    add_code_block(
        '贝壳：300套列表 → 客户选择困难\nH5：  8套精选 + 上榜理由 → 客户信任你的眼光\n      ↓\n     "榜单只放了几套，微信上还有更多"\n      ↓\n      冰山效应：暗示你手上的资源远不止这些'
    )

    pdf.ln(3)
    add_sub_title("内容飞轮")
    add_code_block("拍探房视频 → 视频号/抖音/小红书\n    ↓\n视频挂公众号文章 → 文章放H5入口\n    ↓\nH5精选推荐 + 知识库\n    ↓\n加微信 → 成交\n    ↓\n客户好评 → 新的内容素材 → 🔄 回到第一步")

    pdf.ln(3)
    add_sub_title("为什么璧山短视频是蓝海？")
    add_body("全国房产短视频：几百万人在做")
    add_body("璧山认真做本地房产内容的：可能不到 10 人")
    add_body("有 11 年璧山经验 + 能做出专业判断的：可能只有这一个")
    add_body("前期 200 播放够了，关键是精准触达璧山买房人群")

    # ---- Section 7: 推广渠道 ----
    toc_items[6] = ("七、推广渠道盘点", pdf.page_no())
    pdf.add_page()
    add_section_title("七", "推广渠道盘点")

    add_sub_title("微信生态内（核心）")
    add_table(
        ["渠道", "方式", "挂链接"],
        [
            ["朋友圈", '每天1条“今日好房卡片”+H5链接', "✅"],
            ["微信群", '业主群/买房群分享“璧山好房地图”', "✅"],
            ["1v1私聊", "客户咨询时发链接", "✅"],
            ["视频号", "探房视频 → 挂公众号文章 → 文章放H5", "✅ 间接"],
            ["公众号", '楼市分析 → 文末“查看完整房源”', "✅"],
        ],
        [30, 114, 30],
    )

    pdf.ln(3)
    add_sub_title("链接合规说明")
    add_body("❌ 视频评论区直接留电话/微信 → 可能违规")
    add_body("✅ 视频评论区放 H5 网页链接 → 是内容分享，不违规")
    add_body("H5 是平台和你之间的缓冲层，联系方式在你自己网站里，平台管不到")

    pdf.ln(3)
    add_sub_title("执行节奏")
    add_table(
        ["月份", "重点"],
        [
            ["第1月", "H5上线 + 朋友圈激活已有好友"],
            ["第2月", "视频号一周2条探房"],
            ["第3月", "公众号一周1篇深度分析"],
            ["第4月", "复制内容到小红书/抖音"],
        ],
        [40, 140],
    )

    # ---- Section 8: 待讨论问题 ----
    toc_items[7] = ("八、待和经纪人讨论的问题", pdf.page_no())
    pdf.add_page()
    add_section_title("八", "待和经纪人讨论的问题")

    questions = [
        ("问题 1", "客户最大的痛点是什么？",
         ["看不懂璧山各板块的区别？", "不知道某个小区真实值多少？", "怕买到串串房？",
          "不知道哪个小区对口哪个学校？", "看房跑来跑去太累？", "其他？"]),
        ("问题 2", "房源怎么展示？",
         ["公开层：小区名称、均价区间、户型面积、经纪人点评",
          '概数层："本小区在售约X套"',
          "私域层：具体房源信息、业主底价"]),
        ("问题 3", "串串房怎么处理？",
         ['不做“串串房专区”（避免贴标签）',
          '用中性“装修来源”标签：业主自住装修/翻新装修/开发商精装/毛坯',
          '知识库里写“怎么看翻新质量”类文章']),
        ("问题 4", "还有什么客户需求？",
         ['"我家房子现在值多少"（业主估价）',
          "降价提醒（关注某小区降价通知）",
          "预约集中看房（凑够几个人一起看）",
          "视频/VR看房"]),
        ("问题 5", "经纪人怎么维护内容？",
         ["直接在网页后台编辑？", "告诉开发者内容，帮忙更新？", "用AI生成初稿，经纪人审核修改后发布？"]),
    ]

    for num, title, items in questions:
        add_sub_title(f"{num}：{title}")
        for item in items:
            add_body(f"  · {item}")
        pdf.ln(2)

    # ---- Section 9: 成本 ----
    toc_items[8] = ("九、成本", pdf.page_no())
    pdf.add_page()
    add_section_title("九", "成本")

    add_table(
        ["项目", "费用"],
        [
            ["H5 网页托管", "免费（GitHub Pages）"],
            ["域名", "¥60/年（后面再买）"],
            ["AI 接口", "免费（DeepSeek 免费额度）"],
            ["开发", "0元（AI 写代码）"],
            ["合计", "暂时 0 元"],
        ],
        [80, 100],
    )

    # ---- Section 10: 下一步 ----
    toc_items[9] = ("十、下一步", pdf.page_no())
    pdf.add_page()
    add_section_title("十", "下一步")

    steps = [
        "1. 明天和经纪人讨论以上问题",
        "2. 收集她的反馈，更新方案",
        "3. 开始写代码，先做一个能用的版本",
        "4. 测试 → 她实际使用 → 迭代优化",
    ]
    for s in steps:
        add_body(s)

    pdf.ln(6)
    add_highlight_box(
        "💡 讨论目标：找到 1-2 个最痛的客户痛点，H5 先集中解决。小而精，不要什么都做。\n\n🎯 核心定位：不做“小贝壳”，做小平的“个人 IP 官网”——一个链接，跨平台汇聚客户。\nAI 数字分身 24h 前台接待，需求卡片精准转化，小平微信深度服务。\n贝壳卖信息，你卖判断。买房最终是人对人的信任。",
        "primary",
    )

    # ---- Now add TOC with correct page numbers ----
    # (We rebuild — insert TOC after cover by reordering)
    # For simplicity, we'll add TOC at the end as appendix or just output as-is

    # Save
    pdf.output(output_path)
    print(f"✅ PDF 已生成: {output_path}")
    return True


# ============================================================
# PPT 生成 (python-pptx)
# ============================================================
def generate_ppt(md_content, output_path):
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu, Cm
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE

    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)

    # Color helpers
    def rgb(color_key):
        c = COLORS[color_key]
        return RGBColor(c[0], c[1], c[2])

    def add_bg(slide, color_key="bg_white"):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = rgb(color_key)

    def add_shape_bg(slide, left, top, width, height, color_key):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(color_key)
        shape.line.fill.background()
        return shape

    def add_text_box(
        slide, left, top, width, height, text, font_size=14, color="text_dark",
        bold=False, alignment=PP_ALIGN.LEFT, font_name="Microsoft YaHei"
    ):
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.color.rgb = rgb(color)
        p.font.bold = bold
        p.font.name = font_name
        p.alignment = alignment
        return tf

    def add_multiline_box(
        slide, left, top, width, height, lines, font_size=12, color="text_dark",
        bold_first=False, line_spacing=1.3
    ):
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True

        for i, line_text in enumerate(lines):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = line_text
            p.font.size = Pt(font_size)
            p.font.color.rgb = rgb(color)
            p.font.name = "Microsoft YaHei"
            p.space_after = Pt(font_size * (line_spacing - 1))
            if bold_first and i == 0:
                p.font.bold = True
        return tf

    def add_card(slide, left, top, width, height, title, lines, title_color="primary"):
        """Add a card with colored top bar"""
        card_bg = add_shape_bg(slide, left, top, width, height, "card_bg")
        top_bar = add_shape_bg(slide, left, top, width, Pt(6), title_color)

        add_text_box(
            slide, left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4),
            title, font_size=13, color="text_dark", bold=True
        )
        add_multiline_box(
            slide, left + Inches(0.25), top + Inches(0.55), width - Inches(0.5),
            height - Inches(0.65), lines, font_size=10, color="text_gray"
        )

    # ========================
    # Slide 1: Title
    # ========================
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    add_bg(slide, "bg_light")

    # Top green bar
    add_shape_bg(slide, Inches(0), Inches(0), Inches(13.333), Inches(2.2), "primary")
    add_shape_bg(slide, Inches(0), Inches(2.2), Inches(13.333), Pt(6), "accent")

    add_text_box(slide, Inches(1), Inches(0.6), Inches(11.333), Inches(0.8),
                 "璧山好房", font_size=48, color="bg_white", bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, Inches(1), Inches(1.4), Inches(11.333), Inches(0.5),
                 "独立经纪人小平 · 个人 IP 官网   |   方案讨论稿",
                 font_size=18, color="bg_white", alignment=PP_ALIGN.CENTER)

    add_text_box(slide, Inches(1), Inches(2.8), Inches(11.333), Inches(0.6),
                 "个人电子名片 + 可移动智能前台 = 经纪人的个人 IP 官网",
                 font_size=22, color="primary_dark", bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, Inches(1), Inches(3.4), Inches(11.333), Inches(0.5),
                 "一个链接，发到哪都能打开，跨平台汇聚客户",
                 font_size=15, color="text_gray", alignment=PP_ALIGN.CENTER)

    # Bottom key numbers
    cards_data = [
        ("0 元", "启动成本", "accent"),
        ("24h × 7天", "AI 数字分身值守", "primary"),
        ("1 个链接", "全平台通用", "warm"),
        ("11 年", "璧山本地经验", "purple"),
    ]
    card_w = Inches(2.4)
    card_h = Inches(1.6)
    start_x = Inches(1.5)
    y = Inches(4.6)
    for i, (num, label, color) in enumerate(cards_data):
        x = start_x + i * (card_w + Inches(0.4))
        add_card(slide, x, y, card_w, card_h, num, [label], title_color=color)

    # ========================
    # Slide 2: 思维导图
    # ========================
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, "bg_white")
    add_shape_bg(slide, Inches(0), Inches(0), Inches(13.333), Pt(4), "primary")
    add_text_box(slide, Inches(0.5), Inches(0.2), Inches(12.333), Inches(0.7),
                 "项目全景 · 思维导图", font_size=28, color="primary_dark", bold=True)

    # Center node text
    add_text_box(slide, Inches(4.2), Inches(1.0), Inches(5), Inches(0.7),
                 "🏠 璧山好房 · 小平个人IP官网",
                 font_size=18, color="primary", bold=True, alignment=PP_ALIGN.CENTER)

    # Main branches as cards
    branches_left = [
        ("🎙️ 语音首页", "按住说话 → AI自动分流"),
        ("🤖 AI数字分身", "小平的语调和判断对话"),
        ("🏆 精选匹配", "刚需/改善双通道上榜"),
        ("📋 需求卡片", "加微信前需求画像汇总"),
        ("💬 温暖转化", '不说“登录注册”，自然加微信'),
    ]
    branches_right = [
        ("🗺️ 地图看房", "板块色块 + 楼盘标注"),
        ("📊 楼盘详情", "四级分层 + 价格走势"),
        ("📝 知识库", "按人群标签匹配文章"),
        ("🖥️ 经纪人后台", "数据看板 + 编辑 + 留资管理"),
        ("📱 PWA离线", "添加到主屏幕，离线可看"),
    ]

    card_w_left = Inches(3.6)
    card_h = Inches(0.75)
    for i, (title, desc) in enumerate(branches_left):
        y = Inches(1.8) + i * Inches(0.85)
        add_card(slide, Inches(0.3), y, card_w_left, card_h, title, [desc])

    for i, (title, desc) in enumerate(branches_right):
        y = Inches(1.8) + i * Inches(0.85)
        add_card(slide, Inches(9.4), y, card_w_left, card_h, title, [desc])

    # Center bottom: key differentiators
    add_text_box(slide, Inches(1.5), Inches(6.2), Inches(10.333), Inches(0.5),
                 "贝壳 = 超市（卖信息）  |  小平H5 = 私厨（卖判断）  |  买房最终是人对人的信任",
                 font_size=14, color="warm", bold=True, alignment=PP_ALIGN.CENTER)

    # ========================
    # Slide 3: 目录
    # ========================
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, "bg_light")
    add_shape_bg(slide, Inches(0), Inches(0), Inches(13.333), Pt(4), "primary")
    add_text_box(slide, Inches(0.5), Inches(0.3), Inches(12.333), Inches(0.8),
                 "目  录", font_size=32, color="primary_dark", bold=True, alignment=PP_ALIGN.CENTER)

    toc = [
        ("一", "这是什么？", "产品定义与核心定位"),
        ("二", "客户使用流程", "5步语音→AI→需求卡片→微信转化"),
        ("三", "用户分群策略", "刚需(40-70万) + 改善(80-150万) 双线并行"),
        ("四", "为什么这个模式不一样？", "贝壳 vs 公众号 vs 个人IP官网 三轮对比"),
        ("五", "主要功能模块", "7大模块一览"),
        ("六", "经纪人 IP 生态", "内容飞轮 + 短视频蓝海"),
        ("七", "推广渠道盘点", "微信生态5渠道 + 执行节奏"),
        ("八", "待和经纪人讨论的问题", "5个关键议题"),
        ("九", "成本", "0元启动"),
        ("十", "下一步", "讨论 → 反馈 → 开发 → 迭代"),
    ]

    for i, (num, title, desc) in enumerate(toc):
        y = Inches(1.5) + i * Inches(0.55)
        num_shape = add_shape_bg(slide, Inches(1.2), y, Inches(0.55), Inches(0.45), "primary")
        add_text_box(slide, Inches(1.2), y + Pt(2), Inches(0.55), Inches(0.4),
                     num, font_size=16, color="bg_white", bold=True, alignment=PP_ALIGN.CENTER)
        add_text_box(slide, Inches(2.0), y + Pt(2), Inches(4.5), Inches(0.4),
                     title, font_size=15, color="text_dark", bold=True)
        add_text_box(slide, Inches(6.5), y + Pt(3), Inches(6), Inches(0.4),
                     desc, font_size=11, color="text_gray")

    # ========================
    # Slides 4-13: Content sections
    # ========================
    sections = [
        ("一", "这是什么？", [
            ("", "一个响应式网页（手机+电脑自适应），微信里点开就能用，不用下载 App。"),
            ("", ""),
            ("核心公式", "个人电子名片 + 可移动智能前台 = 经纪人的个人 IP 官网"),
            ("", ""),
            ("三大支柱", ""),
            ("▸ 电子名片", "一个链接，发到哪都能打开，展示你的专业度"),
            ("▸ 智能前台", "24h×7天，AI替你接客，语音+匹配+引导"),
            ("▸ IP 官网", "不是贝壳的分支，是你自己的品牌主页。数据是你的。"),
            ("", ""),
            ("布局", "手机打开=客户版（语音找房）/ 电脑打开=经纪人版（数据管理）"),
        ]),
    ]

    def make_content_slide(title_num, title_text, bullets):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        add_bg(slide, "bg_white")
        add_shape_bg(slide, Inches(0), Inches(0), Inches(13.333), Pt(4), "primary")
        add_text_box(slide, Inches(0.8), Inches(0.3), Inches(11.733), Inches(0.7),
                     f"{title_num}  {title_text}", font_size=28, color="primary_dark", bold=True)

        y = Inches(1.4)
        for label, text in bullets:
            if label == "" and text == "":
                y += Inches(0.2)
                continue
            if label:
                add_text_box(slide, Inches(1.0), y, Inches(11.333), Inches(0.45),
                             label, font_size=16, color="primary", bold=True)
                y += Inches(0.45)
            if text:
                add_text_box(slide, Inches(1.3), y, Inches(11.0), Inches(0.4),
                             text, font_size=12, color="text_dark")
                y += Inches(0.4)
        return slide

    # All sections content
    all_sections = [
        ("二", "客户使用流程（五步）", [
            ("用户旅程", "🎙️语音首页 → AI深度对话 → 精选匹配 → 📋需求卡片 → 💬温暖转化加微信"),
            ("", ""),
            ("第一步：语音首页", "按住说话，AI自动识别刚需/改善，DeepSeek提取预算/户型/位置"),
            ("", "💡 AI是经纪人的数字分身，用小平的语调和判断回复，像跟懂行的朋友聊天"),
            ("第二步：AI深度对话+精选榜", "AI先反问了解需求，再推荐精选房源+上榜理由+经纪人备注"),
            ("", '示例："璧泉60万买三房可以的，我在那边经手过好几套。你主要是自住还是考虑学区？"'),
            ("🆕 第三步：需求卡片", "加微信前弹出需求画像卡片（类型/预算/户型/区域/关注点/补充留言）"),
            ("", '按钮：“发给小平，她已经在看了” → 小金加微信第一句话就精准'),
            ("第四步：楼盘详情", "小区信息+价格走势+经纪人点评+同小区在售概数→冰山效应"),
            ("第五步：温暖转化", '主按钮“找小平进一步了解”，次按钮“留个电话，小平帮你留意降价”'),
            ("", '⚠️ 全程不用“登录”“注册”“提交”'),
        ]),
        ("三", "用户分群策略：刚需+改善双线并行", [
            ("刚需 (40-70万)", "璧山最大群体，决策快，怕买亏/踩坑，对中介依赖高，分享意愿高"),
            ("改善 (80-150万)", "稳定增长，决策中等，怕换得不够好，需专业判断，家庭用户"),
            ("策略", "首页不区分，语音识别后AI自动分流。两条线共享知识库，推荐榜单不同"),
            ("知识库标签", '刚需专属："首付最低多少" · 改善专属："换房先买还是先卖" · 共有："学区房盘点"'),
        ]),
        ("四-1", "为什么不一样？贝壳 vs H5", [
            ("核心差异", '贝壳=超市（自己挑），H5=私厨（帮你配菜）。璧山熟人社会，私厨更竞争力。'),
            ("", ""),
            ("贝壳能做到", "300套列表 / 算法推荐 / 20个经纪人竞争 / 数据归平台 / 通用AI / 房源透明"),
            ("贝壳永远做不到", "8套精选+上榜理由 / 人推荐 / 客户关系独占 / 数据归你 / 你的AI喂你的判断"),
            ("", ""),
            ("根本区别", "贝壳卖信息→客户自己判断→选谁成交都可以"),
            ("", "你卖判断→客户信任你的眼光→只找你成交"),
            ("", "贝壳做标准化，你做个性化。贝壳做广度，你做深度。"),
            ("金句", "买房最终是人对人的信任，不是人对平台的搜索。"),
        ]),
        ("四-2", "公众号 vs H5", [
            ("角色差异", '公众号=广播站（你喊话→订阅者听到→看完走了）'),
            ("", 'H5=智能前台（客户带需求进来→AI 1v1接待→自己探索→加微信）'),
            ("", ""),
            ("公众号优势", "推送能力（模板消息、群发）· 粉丝沉淀"),
            ("H5优势", "语音交互 · 个性化匹配 · 深度行为数据 · 不限功能入口 · 分享即传播"),
            ("", ""),
            ("关键差异", '公众号让你知道“有人看了文章”，H5让你知道“他在找什么样的家”。'),
            ("关系", '不是替代，是互补。公众号负责“拉客”，H5负责“接客”。先做H5，后绑公众号。'),
        ]),
        ("四-3", "产品定义：个人IP官网", [
            ("统一定位", "个人电子名片 + 可移动智能前台 = 经纪人的个人IP官网"),
            ("", ""),
            ("一个产品，两端使用", ""),
            ("📱 移动端（客户看）", "语音入口 + AI匹配 + 精选榜 + 知识库 + 加微信"),
            ("🖥️ 桌面端（小平看）", "地图管理 + 数据编辑 + 留资查看 + AI助手"),
            ("", "同一套代码，同一份数据，根据屏幕大小自动适配"),
            ("", ""),
            ("四级信息分层", ""),
            ("🟢 公开层", "小区名称、均价、户型、经纪人点评 → 所有人"),
            ("🟡 概数层", '"本小区在售约X套" → 所有人（勾起好奇心）'),
            ("🔒 留资层", "完整房源列表、楼层朝向 → 加微信/留电话后"),
            ("🔐 微信层", "业主底价、急售、约看时间 → 微信1v1"),
        ]),
        ("五", "主要功能模块（7大模块）", [
            ("🎙️ 语音找房", "说话就能搜房，不用打字"),
            ("🤖 AI数字分身", "用小平的语调和判断对话，24h前台接待"),
            ("🗺️ 地图看房", "板块色块+楼盘标注，快速了解璧山"),
            ("📊 楼盘详情", "均价、走势、配套、经纪人独家点评"),
            ("📋 需求卡片", "加微信前自动汇总需求画像，第一句话就精准"),
            ("📝 看房知识库", "板块分析、验房技巧、选房攻略（按人群标签）"),
            ("💬 温暖转化", '不说“登录注册”，自然引导加微信'),
        ]),
        ("六", "经纪人IP生态", [
            ("不只是工具，是品牌", "H5给朋友圈装上24h运转的发动机。客户主动探索→加微信时已信任你。"),
            ("", ""),
            ("精选上榜 = 把经验变成产品", '贝壳300套→选择困难 / H5 8套+上榜理由→信任眼光'),
            ("", '"榜单只放了几套，微信上还有更多" → 冰山效应'),
            ("", ""),
            ("内容飞轮", '拍视频→视频号/抖音→挂文章→H5入口→加微信→成交→好评→🔄循环'),
            ("璧山短视频蓝海", "全国几百万人在做 / 璧山认真做的不到10人 / 11年经验只此一个"),
            ("", "前期200播放够了，关键是精准触达璧山买房人群"),
        ]),
        ("七", "推广渠道盘点", [
            ("微信生态5渠道", ""),
            ("朋友圈", '每天1条“今日好房卡片”+H5链接 ✅'),
            ("微信群", '业主群/买房群分享“璧山好房地图” ✅'),
            ("1v1私聊", "客户咨询时发链接 ✅"),
            ("视频号", "探房视频→挂公众号文章→文章放H5 ✅"),
            ("公众号", '楼市分析→文末“查看完整房源” ✅'),
            ("", ""),
            ("链接合规", '❌视频评论留电话/微信→违规  ✅留H5链接→内容分享，不违规'),
            ("执行节奏", "第1月H5上线+朋友圈 · 第2月视频号 · 第3月公众号 · 第4月小红书/抖音"),
        ]),
        ("八", "待和经纪人讨论的5个问题", [
            ("问题1：客户痛点", "看不懂板块？不知道真实价格？怕串串房？不知对口学校？看房太累？"),
            ("问题2：房源展示", "公开层（小区信息）→概数层（在售约X套）→私域层（具体房源），合理吗？"),
            ("问题3：串串房", '不做专区避免贴标签，用中性“装修来源”标签，知识库写翻新质量判断'),
            ("问题4：额外需求", "业主估价？降价提醒？集中看房？视频/VR看房？排优先级？"),
            ("问题5：内容维护", "网页后台编辑？告诉开发者更新？AI生成初稿+经纪人审核？"),
        ]),
        ("九", "成本", [
            ("H5网页托管", "免费（GitHub Pages）"),
            ("域名", "¥60/年（后面再买）"),
            ("AI接口", "免费（DeepSeek免费额度）"),
            ("开发", "0元（AI写代码）"),
            ("合计", "暂时 0 元"),
        ]),
        ("十", "下一步", [
            ("1", "明天和经纪人讨论以上问题"),
            ("2", "收集她的反馈，更新方案"),
            ("3", "开始写代码，先做一个能用的版本"),
            ("4", "测试 → 实际使用 → 迭代优化"),
            ("", ""),
            ("讨论目标", "找到1-2个最痛的客户痛点，H5先集中解决。小而精。"),
            ("核心定位", '不做“小贝壳”，做小平的"个人IP官网"。AI数字分身24h前台，需求卡片精准转化。'),
            ("", "贝壳卖信息，你卖判断。买房最终是人对人的信任。"),
        ]),
    ]

    for num, title, bullets in all_sections:
        make_content_slide(num, title, bullets)

    # ========================
    # Final slide: Thank you
    # ========================
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, "primary")
    add_text_box(slide, Inches(1), Inches(1.5), Inches(11.333), Inches(1),
                 "感谢阅读", font_size=42, color="bg_white", bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, Inches(1), Inches(2.8), Inches(11.333), Inches(0.8),
                 "璧山好房 · 方案讨论稿", font_size=22, color="bg_white", alignment=PP_ALIGN.CENTER)
    add_text_box(slide, Inches(1), Inches(3.8), Inches(11.333), Inches(0.6),
                 "个人电子名片 + 可移动智能前台 = 经纪人的个人 IP 官网",
                 font_size=16, color="bg_white", alignment=PP_ALIGN.CENTER)
    add_text_box(slide, Inches(1), Inches(5.0), Inches(11.333), Inches(0.6),
                 "项目代号：BishanNest  |  成本：0元启动  |  技术：响应式网页 + DeepSeek AI",
                 font_size=12, color="bg_white", alignment=PP_ALIGN.CENTER)

    prs.save(output_path)
    print(f"✅ PPT 已生成: {output_path}")
    return True


# ============================================================
# Main
# ============================================================
def main():
    base = Path(__file__).parent.parent
    md_path = base / "PlanB-方案讨论.md"
    pdf_path = base / "璧山好房_方案讨论.pdf"
    ppt_path = base / "璧山好房_方案讨论.pptx"

    print(f"📖 读取: {md_path}")
    md_content = read_md(md_path)
    print(f"   共 {len(md_content)} 字符")

    print("\n📄 生成 PDF...")
    try:
        generate_pdf(md_content, str(pdf_path))
    except Exception as e:
        print(f"   ⚠️ PDF 生成失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n📊 生成 PPT...")
    try:
        generate_ppt(md_content, str(ppt_path))
    except Exception as e:
        print(f"   ⚠️ PPT 生成失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n🎉 完成！")


if __name__ == "__main__":
    main()
