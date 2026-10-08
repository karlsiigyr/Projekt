"""Writes ../eelvaade.html: one self-contained page (logos inline, mockups embedded)
for choosing between the two directions. Run after build.py and mockups/shoot.mjs."""
import base64
import io
import os
import re

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

GOLD = "#C2A36B"
INK = "#141414"
IVORY = "#F4EFE6"
NIGHT = "#121212"


def svg(folder, name, color, cls=""):
    """Inline a built logo, recoloured."""
    text = open(os.path.join(ROOT, folder, f"{name}-must.svg")).read()
    vb = re.search(r'viewBox="([^"]+)"', text).group(1)
    d = re.search(r' d="([^"]+)"', text).group(1)
    return (f'<svg class="{cls}" viewBox="{vb}" role="img" aria-label="Leola meestejuuksur">'
            f'<path fill="{color}" d="{d}"/></svg>')


def jpg(name, width=1600):
    im = Image.open(os.path.join(ROOT, "eelvaated", name)).convert("RGB")
    im.thumbnail((width, width * 2))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=84, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def direction(key, folder, prefix, title, kicker, blurb, recommended=False):
    badge = '<span class="badge">soovitus</span>' if recommended else ""
    return f"""
<section class="dir" id="{key}">
  <div class="dir-head">
    <p class="kicker">{kicker}</p>
    <h2>{title}{badge}</h2>
    <p class="lead">{blurb}</p>
  </div>
  <div class="duo">
    <figure class="panel night">{svg(folder, prefix, GOLD, "main")}</figure>
    <figure class="panel ivory">{svg(folder, prefix, INK, "main")}</figure>
  </div>
  <div class="mock">
    <figure class="shot door"><img src="{jpg(f'{key}-uks.jpg', 1200)}" alt="Logo klaasuksel"><figcaption>Uks: kuldne kile klaasil, kõrval vertikaalne riba, üleval silt</figcaption></figure>
    <figure class="shot web"><img src="{jpg(f'{key}-veeb.jpg', 1600)}" alt="Logo veebilehel"><figcaption>Veebileht: päises nimi, sakis favicon</figcaption></figure>
  </div>
  <div class="variants">
    <figure class="panel ivory"><div class="slot wide">{svg(folder, prefix + '-nimi', INK)}</div><figcaption>Ainult nimi</figcaption></figure>
    <figure class="panel night"><div class="slot tall">{svg(folder, prefix + '-vertikaalne', GOLD)}</div><figcaption>Vertikaalne</figcaption></figure>
    <figure class="panel ivory"><div class="slot square">{svg(folder, prefix + '-pitser', INK)}</div><figcaption>Pitser</figcaption></figure>
    <figure class="panel night"><div class="slot square mark">{svg(folder, prefix + '-L', GOLD)}</div><figcaption>L-märk / favicon</figcaption></figure>
  </div>
</section>"""


PAGE = """<!doctype html>
<html lang="et">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Leola logo kavand</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..900;1,6..96,400..900&display=swap" rel="stylesheet">
<style>
/* Dark showroom on purpose: the identity is gold on black, so the page stays in that one look.
   Layout: one centred column; each direction = logo pair, mockups, variant strip. */
:root {
  color-scheme: dark;
  --bg: #0e0e0e; --ink: #efe8da; --muted: rgba(239,232,218,.62);
  --gold: #c2a36b; --line: rgba(194,163,107,.28); --ivory: #f4efe6; --night: #121212; --ink-dark: #151515;
  --serif: 'Bodoni Moda', 'Bodoni 72', Didot, 'Times New Roman', serif;
  --mono: ui-monospace, Menlo, Consolas, monospace;
}
* { box-sizing: border-box; }
html { background: var(--bg); }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--serif);
       font-optical-sizing: auto; -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1180px; margin-inline: auto; padding-inline: clamp(16px, 4vw, 28px); padding-block: 0; }
a:focus-visible { outline: 2px solid var(--gold); outline-offset: 4px; }
h1, h2 { text-wrap: balance; }
.duo > *, .mock > *, .info > *, .variants > * { min-width: 0; }
.kicker { font-size: 12px; letter-spacing: .32em; text-transform: uppercase; color: var(--gold); margin: 0 0 18px;
          font-variation-settings: 'opsz' 6; font-weight: 600; }
header.top { padding: 96px 0 64px; border-bottom: 1px solid var(--line); }
h1 { font-style: italic; font-weight: 700; font-size: clamp(44px, 7vw, 88px); line-height: 1; margin: 0 0 26px; letter-spacing: -.01em;
     font-variation-settings: 'opsz' 60; }
h2 { font-style: italic; font-weight: 700; font-size: clamp(34px, 4.4vw, 54px); margin: 0 0 14px; line-height: 1.05;
     font-variation-settings: 'opsz' 48; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
h3 { font-weight: 600; font-size: 13px; letter-spacing: .3em; text-transform: uppercase; color: var(--gold); margin: 0 0 22px;
     font-variation-settings: 'opsz' 6; }
p, li, td { font-size: 18px; line-height: 1.65; font-variation-settings: 'opsz' 11; }
.lead { color: var(--muted); max-width: 62ch; margin: 0; }
.badge { font-style: normal; font-size: 11px; letter-spacing: .28em; text-transform: uppercase; border: 1px solid var(--gold);
         color: var(--gold); padding: 7px 12px 6px; font-weight: 600; font-variation-settings: 'opsz' 6; }
.jump { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 34px; }
.jump a { color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--gold); padding-bottom: 5px; font-size: 13px;
          letter-spacing: .26em; text-transform: uppercase; font-weight: 600; font-variation-settings: 'opsz' 6; margin-right: 22px; }
section.dir { padding: 88px 0; border-bottom: 1px solid var(--line); }
.dir-head { margin-bottom: 40px; }
figure { margin: 0; }
.panel { border: 1px solid var(--line); display: flex; flex-direction: column; align-items: center; justify-content: center; }
.panel.night { background: var(--night); }
.panel.ivory { background: var(--ivory); color: var(--ink-dark); }
.duo { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.duo .panel { aspect-ratio: 3 / 2; max-width: 100%; padding: 9%; }
.duo svg.main { width: 100%; height: 100%; }
.mock { display: grid; grid-template-columns: 1fr 1.6fr; gap: 18px; margin-top: 18px; align-items: start; }
.shot img { width: 100%; display: block; border: 1px solid var(--line); }
figcaption { font-size: 12px; letter-spacing: .14em; color: var(--muted); margin-top: 12px; text-transform: uppercase;
             font-variation-settings: 'opsz' 6; font-weight: 500; text-align: left; align-self: flex-start; }
.panel figcaption { align-self: center; color: inherit; opacity: .55; margin: 16px 0 0; }
.variants { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin-top: 18px; }
.variants .panel { padding: 26px 22px 18px; }
.slot { width: 100%; display: flex; align-items: center; justify-content: center; height: 220px; }
.slot svg { max-width: 100%; max-height: 100%; }
.slot.wide svg { width: 100%; } .slot.tall svg { height: 92%; } .slot.square svg { height: 88%; }
.slot.mark svg { max-width: 78%; height: 78%; }
.info { padding: 88px 0; display: grid; grid-template-columns: 1fr 1fr; gap: 56px; border-bottom: 1px solid var(--line); }
.swatches { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.sw { border: 1px solid var(--line); }
.sw i { display: block; aspect-ratio: 4 / 3; }
.sw b { display: block; padding: 12px 14px 4px; font-size: 15px; font-weight: 600; font-variation-settings: 'opsz' 11; }
.sw code { display: block; padding: 0 14px 14px; font: 13px/1.4 var(--mono); color: var(--muted); }
.table { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
td { padding: 12px 0; border-bottom: 1px solid var(--line); vertical-align: top; font-size: 16px; }
td:first-child { color: var(--muted); padding-right: 20px; width: 42%; }
td code, li code { font: 13px/1.5 var(--mono); color: var(--ink); word-break: break-word; }
ul { margin: 0; padding-left: 20px; }
li { margin-bottom: 10px; font-size: 16px; }
footer { padding: 48px 0 80px; color: var(--muted); font-size: 13px; letter-spacing: .14em; text-transform: uppercase;
         font-variation-settings: 'opsz' 6; }
@media (max-width: 860px) {
  .duo, .mock, .info { grid-template-columns: 1fr; }
  .variants { grid-template-columns: 1fr 1fr; }
  .slot { height: 160px; }
  header.top { padding: 64px 0 44px; } section.dir, .info { padding: 60px 0; }
}
@media (max-width: 480px) {
  .variants { grid-template-columns: 1fr; }
  .swatches { grid-template-columns: 1fr 1fr; }
}
</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <p class="kicker">Leola meestejuuksur · Viljandi</p>
  <h1>Logo kavand</h1>
  <p class="lead">Kaks suunda. <b>A</b> on puhas, käekirjaline nimi. <b>B</b> on arendatud edasi inspiratsioonipildist
  ja selle L-täht on ühtlasi avatud käärid. Püstkriips ja jalg on terad, kruvi on nurgas. Mõlemad logod on ühes värvis
  ja töötavad kullana mustal, mustana heledal ning valgena klaasil.</p>
  <div class="jump"><a href="#klassik">A · Klassik</a><a href="#kaarid">B · Käärid</a><a href="#failid">Failid</a></div>
</header>
%DIRS%
<section class="info" id="failid">
  <div>
    <h3>Värvid</h3>
    <div class="swatches">
      <div class="sw"><i style="background:#141414"></i><b>Must</b><code>#141414</code></div>
      <div class="sw"><i style="background:#C2A36B"></i><b>Kuld</b><code>#C2A36B</code></div>
      <div class="sw"><i style="background:#F4EFE6"></i><b>Kreem</b><code>#F4EFE6</code></div>
    </div>
    <h3 style="margin-top:44px">Uksele (kleebiste tegijale)</h3>
    <ul>
      <li>SVG-failid on puhtad vektorkontuurid, fonte pole vaja. Üks värv, sobib otse lõikeplotterile.</li>
      <li>Väikseim mõistlik laius lõigatud kilena: A põhilogo ~45 cm, B põhilogo ~40 cm. Väiksemaks võta „ainult nimi” fail.</li>
      <li>Kui kile läheb klaasi sisepinnale, peeglib kleebiste tegija faili.</li>
      <li>Kuld: metallik-kuldne kile või lehtkuld. Valge: matt valge kile.</li>
    </ul>
  </div>
  <div>
    <h3>Mis fail kuhu</h3>
    <div class="table"><table>
      <tr><td>Veebilehe päis</td><td><code>…-nimi-kuld.svg</code> tumedal, <code>…-nimi-must.svg</code> heledal</td></tr>
      <tr><td>Uks, aken, silt</td><td><code>leola-…-kuld.svg</code> / <code>-valge.svg</code></td></tr>
      <tr><td>Kitsas riba uksel</td><td><code>…-vertikaalne-….svg</code></td></tr>
      <tr><td>Instagram, Facebook</td><td><code>sotsiaalmeedia/…-profiilipilt.png</code></td></tr>
      <tr><td>Lingi eelvaade</td><td><code>sotsiaalmeedia/…-jagamispilt-1200x630.png</code></td></tr>
      <tr><td>Favicon</td><td><code>favicon/</code> kaust</td></tr>
      <tr><td>Word, Canva jms</td><td><code>png/</code> kaust (läbipaistev taust)</td></tr>
    </table></div>
    <h3 style="margin-top:44px">Fondid</h3>
    <ul>
      <li><b>Bodoni Moda</b>: B nimi ja kõik suurtähed. Tasuta Google Fontsis, sobib ka veebi pealkirjadeks.</li>
      <li><b>Pinyon Script</b>: A nimi. Kasuta ainult logos, mitte tavatekstis.</li>
      <li>Mõlemal SIL Open Font License: tasuta, ka äriliseks kasutuseks ja logos.</li>
    </ul>
  </div>
</section>
<footer>Leola meestejuuksur · logo kavand · näidispiltide tekstid on kohatäited</footer>
</div>
</body>
</html>
"""


def main():
    dirs = direction(
        "klassik", "A-klassik", "leola-klassik", "Klassik", "Suund A · nimi kirjatähtedes",
        "Leola klassikalises kirjafondis, all suurtähtedes MEESTEJUUKSUR ja VILJANDI. "
        "Pidulik ja rahulik, nagu vana rätsepa või juuksuri silt.")
    dirs += direction(
        "kaarid", "B-kaarid", "leola-kaarid", "Käärid", "Suund B · Bodoni kaldkiri ja käärid",
        "Leola kõrge kontrastiga Bodoni kaldkirjas. L-täht on ühtlasi avatud käärid, sõrmerõngad "
        "kasvavad nurgast välja. Eraldi L-märk sobib faviconiks ja profiilipildiks.", recommended=True)
    html = PAGE.replace("%DIRS%", dirs)
    out = os.path.join(ROOT, "eelvaade.html")
    with open(out, "w") as f:
        f.write(html)
    print(out, f"{len(html) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
