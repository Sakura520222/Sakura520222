"""Rebuild the README image with Python and Pillow: python scripts/build_profile.py."""

from base64 import b64decode, b64encode
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from unicodedata import east_asian_width
from xml.etree import ElementTree
from xml.sax.saxutils import escape

from PIL import Image


ASSETS = Path(__file__).resolve().parents[1] / "assets"
WIDTH = 800
INSET = 30
CONTENT_WIDTH = WIDTH - INSET * 2
GAP = 15
CAPTION_FONT = 25
CAPTION_LINE = 32
SVG_NAMESPACE = "http://www.w3.org/2000/svg"


@dataclass(frozen=True)
class Artwork:
    name: str
    caption: str
    description: str


GALLERY = (
    (
        "玉树樱", "初雪樱", "snow",
        (
            (Artwork("tamaki-sakura-classroom", "黑板的相合伞下，写着「はつゆき」和「さくら」", "玉树樱在教室黑板前拿着粉笔"),),
            (
                Artwork("tamaki-sakura-snowmen", "课桌上，两个小雪人共撑一把伞", "玉树樱坐在摆着两个雪人的课桌旁"),
                Artwork("tamaki-sakura-graduation", "「初雪から桜まで　卒業おめでとう」", "玉树樱拿着毕业证书筒，身旁飘着彩纸"),
            ),
            (
                Artwork("tamaki-sakura-strawberry", "樱递来一勺草莓甜点", "玉树樱用勺子托着一颗草莓"),
                Artwork("tamaki-sakura-pajamas", "「キッスタイムではないでしょうか」", "玉树樱穿着浅黄色睡衣，趴在沙发上笑"),
            ),
            (
                Artwork("tamaki-sakura-christmas", "「MERRY CHRISTMAS!」", "玉树樱和兔子穿着圣诞服装"),
                Artwork("tamaki-sakura-karaoke", "白熊「シロクマ、シロクマ男歌いまーすっ」", "玉树樱和朋友们在卡拉 OK 聚会"),
            ),
            (
                Artwork("tamaki-sakura-stage", "演出服、星光和一个Wink", "玉树樱穿紫色演出服，在星光下眨眼比耶"),
                Artwork("tamaki-sakura-summer", "菠萝、扶桑花和夏日装扮", "玉树樱戴着红色花饰，手里拿着菠萝"),
            ),
            (Artwork("tamaki-sakura-bunny", "樱和总陪在她身边的兔子ネム", "玉树樱把一只长耳兔抱在脸旁"),),
        ),
    ),
    (
        "朝武芳乃", "千恋＊万花", "blossom",
        (
            (
                Artwork("tomotake-yoshino-01", "神社檐下，芳乃举刀起舞", "朝武芳乃身着巫女服，在神社举起饰有彩带的短刀"),
                Artwork("tomotake-yoshino-05", "「穗织当地神社的巫女」", "朝武芳乃身着巫女服，双手扶着榻榻米正坐"),
            ),
            (
                Artwork("tomotake-yoshino-03", "朝武芳乃（CV 遥そら），巫女服与表情草图", "朝武芳乃的巫女服插画和表情设定草图"),
                Artwork("tomotake-yoshino-06", "芳乃的巫女服、校服与和装", "朝武芳乃的巫女服、校服、和装和 Q 版造型"),
            ),
            (
                Artwork("tomotake-yoshino-04", "「芳乃描きおろし壁紙」", "朝武芳乃穿蓝绿色校服，双手提着裙摆"),
                Artwork("tomotake-yoshino-07", "夕阳下，芳乃回眸，手还牵着", "朝武芳乃身穿校服，在夕阳下回头与人牵手"),
            ),
            (
                Artwork("tomotake-yoshino-02", "穿着粉色浴衣的芳乃，兽耳露出来了", "穿粉色浴衣的朝武芳乃露出兽耳，神情惊讶"),
                Artwork("tomotake-yoshino-08", "同一身粉色浴衣，芳乃露出浅笑", "穿粉色浴衣、长着兽耳的朝武芳乃露出浅笑"),
            ),
        ),
    ),
    (
        "丛雨", "千恋＊万花", "leaf",
        (
            (Artwork("murasame-03", "「神刀“丛雨丸”的管理者」", "丛雨手持长刀，身旁是表情设定草图"),),
            (
                Artwork("murasame-01", "树影与溪水间，丛雨踏着凉鞋", "丛雨身穿和服，在溪边林间微笑"),
                Artwork("murasame-02", "换上校服的丛雨，牵着手往前跑", "丛雨穿着校服，在林间回头牵手"),
            ),
        ),
    ),
)


STYLE = """
  svg {
    --ink: #332742;
    --muted: #574960;
    --lavender: #6e5488;
    --rose: #9a526d;
    --sage: #476b5e;
    --paper: #f8f4fa;
    --spring: #f3f8f3;
    --hero-start: #f8dfec;
    --hero-end: #e5e9fa;
    --cover-mat: #fff9fd;
    --card: #fffdfd;
    --line: #dfd4e4;
    --image-edge: #000;
    --flake: #fff;
    --petal: #d977a2;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Hiragino Sans", sans-serif;
  }
  text { fill: var(--ink); }
  .title, .character {
    font-family: "Songti SC", "Noto Serif CJK SC", SimSun, serif;
    font-weight: 700;
  }
  .title { font-size: 59px; letter-spacing: 4px; }
  .motto { font-size: 26px; letter-spacing: 3px; fill: var(--muted); }
  .character { font-size: 42px; letter-spacing: 1px; }
  .work { font-size: 25px; fill: var(--accent); }
  .caption { font-size: 23px; fill: var(--muted); }
  .snow { --accent: var(--lavender); }
  .blossom { --accent: var(--rose); }
  .leaf { --accent: var(--sage); }
  .accent { color: var(--accent); fill: currentColor; }
  .card, .mat { stroke: var(--line); }
  .card { fill: var(--card); }
  .mat { fill: var(--cover-mat); }
  .image-edge { fill: none; stroke: var(--image-edge); stroke-opacity: .1; }
  .flake { fill: var(--flake); opacity: .82; animation: drift-snow var(--time) linear var(--delay) infinite; }
  .petal { color: var(--petal); opacity: .58; animation: drift-petal var(--time) ease-in-out var(--delay) infinite; }
  @keyframes drift-snow {
    0% { opacity: 0; transform: translate(-5px, -13px); }
    20%, 73% { opacity: .86; }
    100% { opacity: 0; transform: translate(21px, 49px); }
  }
  @keyframes drift-petal {
    0% { opacity: 0; transform: translate(-9px, -12px) rotate(-18deg); }
    26%, 71% { opacity: .67; }
    100% { opacity: 0; transform: translate(26px, 34px) rotate(58deg); }
  }
  @media (max-width: 480px) {
    .caption { font-size: 25px; }
  }
  @media (prefers-color-scheme: dark) {
    svg {
      --ink: #f5eafa;
      --muted: #e1d1e6;
      --lavender: #d0b8ed;
      --rose: #eda5be;
      --sage: #a9d5b9;
      --paper: #1f1829;
      --spring: #1a2825;
      --hero-start: #432640;
      --hero-end: #262c48;
      --cover-mat: #332a43;
      --card: #2a2234;
      --line: #4f3e5b;
      --image-edge: #fff;
      --flake: #e0dbff;
      --petal: #efa0c4;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .flake, .petal { animation: none; }
  }
"""


DEFINITIONS = """
  <linearGradient id="paper" x2="0" y2="1" gradientUnits="objectBoundingBox">
    <stop stop-color="var(--paper)"/>
    <stop offset="1" stop-color="var(--spring)"/>
  </linearGradient>
  <linearGradient id="hero" x1="0" y1="1" x2="1" y2="0">
    <stop stop-color="var(--hero-start)"/>
    <stop offset="1" stop-color="var(--hero-end)"/>
  </linearGradient>
  <path id="petal" d="M0 8C-6 5-7-2-3-8L0-6 3-8C7-2 6 5 0 8Z" fill="currentColor"/>
  <g id="flower">
    <use href="#petal" y="-7"/>
    <use href="#petal" y="-7" transform="rotate(72)"/>
    <use href="#petal" y="-7" transform="rotate(144)"/>
    <use href="#petal" y="-7" transform="rotate(216)"/>
    <use href="#petal" y="-7" transform="rotate(288)"/>
    <circle r="2.2" fill="var(--card)"/>
  </g>
  <path id="snowflake" d="M0-13v26m-11.26-19.5 22.52 13m-22.52 0 22.52-13M-3-10l3 3 3-3m-3 17-3 3m3-3 3 3" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.9"/>
  <path id="leaf" d="M-14 5C-11-10 4-14 14-12 13 2 4 13-11 11L6-4-14 9Z" fill="currentColor"/>
"""


def image_data(image, max_size):
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    buffer = BytesIO()
    image.save(buffer, "WEBP", quality=88, method=6, icc_profile=image.info.get("icc_profile"))
    return "data:image/webp;base64," + b64encode(buffer.getvalue()).decode("ascii")


def caption_lines(caption, width):
    """Wrap CJK text at glyph boundaries and keep closing punctuation with its text."""
    def token_width(char):
        return CAPTION_FONT * (1 if east_asian_width(char) in "FWA" else 0.62)

    lines = []
    line = ""
    length = 0
    for char in caption:
        advance = token_width(char)
        if line and length + advance > width and char not in "、。，）」』！っー":
            split = len(line)
            if line[-1] in "（「『":
                split -= 1
            lines.append(line[:split].rstrip())
            line = line[split:]
            length = sum(map(token_width, line))
        line += char
        length += advance
    return [*lines, line.strip()]


def hero():
    old_banner = ElementTree.parse(ASSETS / "profile-banner.svg")
    portrait = old_banner.find(f".//{{{SVG_NAMESPACE}}}image").get("href")
    with Image.open(BytesIO(b64decode(portrait.split(",", 1)[1]))) as source:
        portrait_data = image_data(source, (760, 690))

    snow = (
        (39, 38, 3.2, 12, -2), (104, 41, 4, 11, -5), (246, 55, 2.4, 14, -1),
        (360, 85, 3.8, 12, -8), (408, 193, 4.4, 10, -3), (720, 16, 2.8, 13, -6),
        (428, 239, 3.0, 11, -9), (754, 221, 4, 15, -12), (32, 195, 2.5, 12, -9),
    )
    petals = ((377, 206, 0.65, 12, -4), (425, 40, 0.72, 15, -2), (738, 253, 0.74, 13, -8))
    particles = [
        f'<circle class="flake" cx="{x}" cy="{y}" r="{radius}" style="--time:{duration}s;--delay:{delay}s"/>'
        for x, y, radius, duration, delay in snow
    ]
    particles.extend(
        f'<g transform="translate({x} {y}) scale({scale})"><use class="petal" href="#petal" '
        f'style="--time:{duration}s;--delay:{delay}s"/></g>'
        for x, y, scale, duration, delay in petals
    )
    return f"""
<g class="snow">
  <defs><clipPath id="cover-frame"><rect x="454" y="28" width="311" height="243" rx="20"/></clipPath></defs>
  <path d="M28 0H772A28 28 0 0 1 800 28V284H0V28A28 28 0 0 1 28 0Z" fill="url(#hero)"/>
  <g aria-hidden="true">
    <circle cx="587" cy="99" r="173" fill="var(--card)" opacity=".26"/>
    <path d="M0 270C132 240 220 288 367 258S653 216 800 266V284H0Z" fill="var(--card)" opacity=".36"/>
    <path d="M45 95h76" stroke="var(--accent)" stroke-width="1" opacity=".55"/>
    <use href="#flower" class="accent" transform="translate(137 95) scale(.52)" opacity=".76"/>
  </g>
  <rect class="mat" x="447" y="21" width="325" height="257" rx="26"/>
  <image id="cover-art" x="454" y="28" width="311" height="243" preserveAspectRatio="xMidYMin slice"
         clip-path="url(#cover-frame)" href="{portrait_data}"/>
  <rect class="image-edge" x="454" y="28" width="311" height="243" rx="20"/>
  <text class="title" x="43" y="164">车厘子小樱</text>
  <text class="motto" x="46" y="216">始于初雪 · 终于樱</text>
  <g aria-hidden="true">{''.join(particles)}</g>
</g>"""


def section_heading(name, game, theme, y):
    symbol = {"snow": "snowflake", "blossom": "flower", "leaf": "leaf"}[theme]
    return f"""
  <g class="{theme}">
    <use href="#{symbol}" class="accent" transform="translate(50 {y + 26}) scale(.85)" aria-hidden="true"/>
    <text class="character" x="76" y="{y + 40}">{escape(name)}</text>
    <text class="work" x="{WIDTH - INSET}" y="{y + 37}" text-anchor="end">{escape(game)}</text>
    <path d="M{INSET} {y + 58}H{WIDTH - INSET}" stroke="var(--line)"/>
  </g>"""


def gallery_card(art, source, x, y, width, height, lines, caption_height):
    frame = f"frame-{art.name}"
    center = x + width / 2
    spans = "".join(
        f'<tspan x="{center:g}" dy="{0 if index == 0 else CAPTION_LINE}">{escape(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    text_y = y + height + (caption_height - (len(lines) - 1) * CAPTION_LINE) / 2 + 8
    data = image_data(source, (round(width * 1.65), round(height * 1.65)))
    return f"""
  <g id="{art.name}">
    <title>{escape(art.description)}</title>
    <defs><clipPath id="{frame}"><rect x="{x}" y="{y}" width="{width}" height="{height + 14}" rx="15"/></clipPath></defs>
    <rect class="card" x="{x}" y="{y}" width="{width}" height="{height + caption_height}" rx="15"/>
    <image x="{x}" y="{y}" width="{width}" height="{height}" clip-path="url(#{frame})"
           preserveAspectRatio="none" href="{data}"/>
    <rect class="image-edge" x="{x}" y="{y}" width="{width}" height="{height + caption_height}" rx="15"/>
    <text class="caption" x="{center:g}" y="{text_y:g}" text-anchor="middle">{spans}</text>
  </g>"""


def gallery_row(artworks, y):
    sources = [Image.open(ASSETS / f"{art.name}.webp") for art in artworks]
    try:
        aspects = [image.width / image.height for image in sources]
        area = CONTENT_WIDTH - GAP * (len(artworks) - 1)
        if len(artworks) == 1 and aspects[0] < 1.5:
            area = min(area, 610)
        height = round(area / sum(aspects))
        widths = [round(height * aspect) for aspect in aspects[:-1]]
        widths.append(area - sum(widths))
        wrapped = [caption_lines(art.caption, width - 34) for art, width in zip(artworks, widths)]
        caption_height = 56 + CAPTION_LINE * (max(map(len, wrapped)) - 1)
        x = (WIDTH - area - GAP * (len(artworks) - 1)) // 2
        cards = []
        for art, source, width, lines in zip(artworks, sources, widths, wrapped):
            cards.append(gallery_card(art, source, x, y, width, height, lines, caption_height))
            x += width + GAP
        return "".join(cards), y + height + caption_height + GAP
    finally:
        for source in sources:
            source.close()


def main():
    body = [hero()]
    y = 308
    for name, game, theme, rows in GALLERY:
        body.append(section_heading(name, game, theme, y))
        y += 73
        for row in rows:
            markup, y = gallery_row(row, y)
            body.append(markup)
        y += 28

    height = y + 1
    svg = f"""<svg xmlns="{SVG_NAMESPACE}" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}"
     role="img" aria-labelledby="profile-title profile-description">
<title id="profile-title">车厘子小樱</title>
<desc id="profile-description">始于初雪 · 终于樱。玉树樱、朝武芳乃和丛雨的二十一张插画与配文。</desc>
<style>{STYLE}</style>
<defs>{DEFINITIONS}</defs>
<rect width="{WIDTH}" height="{height}" rx="28" fill="url(#paper)"/>
{''.join(body)}
</svg>
"""
    output = ASSETS / "profile.svg"
    output.write_text(svg, encoding="utf-8", newline="\n")
    print(f"{output.name}: {WIDTH} × {height}, {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
