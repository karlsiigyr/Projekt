"""Generates the mockup scenes (HTML) that shoot.mjs turns into ../../eelvaated/*.png.

The scenes reference the finished SVG files, so they always show the real logo.
Texts in the mockups are placeholders, not the shop's real copy.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.dirname(os.path.dirname(HERE))  # .../logo
OUT = os.path.join(HERE, "_html")

FONTS = """
@font-face { font-family: 'Bodoni Moda'; src: url('/allikas/fonts/bodonimoda/BodoniModa[opsz,wght].ttf'); font-weight: 400 900; font-style: normal; }
@font-face { font-family: 'Bodoni Moda'; src: url('/allikas/fonts/bodonimoda/BodoniModa-Italic[opsz,wght].ttf'); font-weight: 400 900; font-style: italic; }
@font-face { font-family: 'Pinyon Script'; src: url('/allikas/fonts/pinyonscript/PinyonScript-Regular.ttf'); }
"""

GOLD_METAL = ("linear-gradient(118deg, #7a5f33 0%, #c4a25f 18%, #f1dfa8 34%, #b8924c 50%, "
              "#e6cf96 64%, #94733d 82%, #d3b778 100%)")

DIRECTIONS = {
    "klassik": dict(folder="A-klassik", prefix="leola-klassik", theme="light"),
    "kaarid": dict(folder="B-kaarid", prefix="leola-kaarid", theme="dark"),
}


def src(d, variant, color):
    c = DIRECTIONS[d]
    v = f"-{variant}" if variant else ""
    return f"/{c['folder']}/{c['prefix']}{v}-{color}.svg"


def web(d):
    c = DIRECTIONS[d]
    dark = c["theme"] == "dark"
    bg, fg = ("#0f0f0f", "#efe8da") if dark else ("#f4efe6", "#151515")
    muted = "rgba(239,232,218,.62)" if dark else "rgba(21,21,21,.62)"
    accent = "#c2a36b" if dark else "#8f7140"
    logo_color = "kuld" if dark else "must"
    seal_color = "kuld" if dark else "must"
    fav = f"/{c['folder']}/favicon/favicon.svg"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ width: 1600px; height: 1000px; background: #2a2a2a; font-family: 'Bodoni Moda', serif; }}
.chrome {{ height: 46px; background: #1d1d1d; display: flex; align-items: flex-end; padding: 0 14px; gap: 10px; }}
.dots {{ display: flex; gap: 8px; align-self: center; margin-right: 10px; }}
.dots i {{ width: 12px; height: 12px; border-radius: 50%; background: #444; display: block; }}
.tab {{ background: {bg}; height: 36px; border-radius: 9px 9px 0 0; padding: 0 18px; display: flex; align-items: center; gap: 10px;
       font: 500 13px/1 system-ui, sans-serif; color: {fg}; width: 260px; }}
.tab img {{ width: 16px; height: 16px; border-radius: 3px; }}
.bar {{ height: 40px; background: {bg}; border-bottom: 1px solid {'#222' if dark else '#e2dccf'}; display: flex; align-items: center; padding: 0 18px; }}
.url {{ height: 26px; border-radius: 13px; flex: 1; background: {'#1b1b1b' if dark else '#ebe5d9'}; }}
.page {{ height: 914px; background: {bg}; color: {fg}; position: relative; overflow: hidden; }}
.page::after {{ content: ''; position: absolute; inset: 0; background: url('/allikas/mockups/myra.png'); opacity: {'.05' if dark else '.035'}; mix-blend-mode: overlay; pointer-events: none; }}
nav {{ display: flex; align-items: center; justify-content: space-between; padding: 34px 90px; }}
nav img {{ height: 64px; }}
nav ul {{ display: flex; gap: 44px; list-style: none; font: 600 13px/1 'Bodoni Moda'; letter-spacing: .26em; font-variation-settings: 'opsz' 6; }}
.btn {{ border: 1.5px solid {accent}; color: {accent}; padding: 15px 26px; font: 600 13px/1 'Bodoni Moda'; letter-spacing: .24em; font-variation-settings: 'opsz' 6; }}
.hero {{ display: grid; grid-template-columns: 1.15fr .85fr; align-items: center; padding: 60px 90px 0; gap: 40px; }}
.kicker {{ font: 600 13px/1 'Bodoni Moda'; letter-spacing: .34em; color: {accent}; font-variation-settings: 'opsz' 6; }}
h1 {{ font: italic 700 92px/1.02 'Bodoni Moda'; font-variation-settings: 'opsz' 48; margin: 28px 0 30px; letter-spacing: -.01em; }}
p {{ font: 400 21px/1.6 'Bodoni Moda'; font-variation-settings: 'opsz' 11; color: {muted}; max-width: 560px; }}
.cta {{ margin-top: 44px; display: flex; gap: 18px; align-items: center; }}
.cta .solid {{ background: {accent}; color: {bg}; padding: 19px 34px; font: 700 13px/1 'Bodoni Moda'; letter-spacing: .26em; font-variation-settings: 'opsz' 6; }}
.cta .ghost {{ font: 600 13px/1 'Bodoni Moda'; letter-spacing: .26em; color: {fg}; border-bottom: 1px solid {accent}; padding-bottom: 6px; font-variation-settings: 'opsz' 6; }}
.art {{ position: relative; height: 640px; display: grid; place-items: center; }}
.art .frame {{ position: absolute; inset: 30px 10px 30px 60px; border: 1px solid {accent}; opacity: .55; }}
.art img {{ width: 420px; opacity: .95; }}
.foot {{ position: absolute; left: 90px; right: 90px; bottom: 34px; display: flex; justify-content: space-between;
        font: 600 12px/1 'Bodoni Moda'; letter-spacing: .3em; color: {muted}; font-variation-settings: 'opsz' 6; }}
</style></head><body>
<div class="chrome"><div class="dots"><i></i><i></i><i></i></div><div class="tab"><img src="{fav}">Leola meestejuuksur</div></div>
<div class="bar"><div class="url"></div></div>
<div class="page">
  <nav><img src="{src(d, 'nimi', logo_color)}" alt="Leola">
    <ul><li>TEENUSED</li><li>HINNAKIRI</li><li>MEIST</li><li>KONTAKT</li></ul>
    <div class="btn">BRONEERI AEG</div></nav>
  <section class="hero">
    <div><div class="kicker">MEESTEJUUKSUR · VILJANDI</div>
      <h1>Klassikaline meeste juukselõikus</h1>
      <p>Siia tuleb lühike tutvustus: kes te olete, mida pakute ja miks tasub tulla.</p>
      <div class="cta"><div class="solid">BRONEERI AEG</div><div class="ghost">VAATA HINNAKIRJA</div></div></div>
    <div class="art"><div class="frame"></div><img src="{src(d, 'pitser', seal_color)}" alt=""></div>
  </section>
  <div class="foot"><span>NÄIDISKUJUNDUS</span><span>LEOLA MEESTEJUUKSUR</span></div>
</div></body></html>"""


def door(d):
    c = DIRECTIONS[d]
    wall = ("repeating-linear-gradient(90deg, #13201b 0 118px, #0f1a16 118px 122px)" if d == "klassik"
            else "repeating-linear-gradient(90deg, #161616 0 118px, #101010 118px 122px)")
    main = src(d, "", "valge")
    strip = src(d, "vertikaalne", "valge")
    fascia = src(d, "nimi", "valge")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ width: 1200px; height: 1500px; background: {wall}; position: relative; overflow: hidden; }}
body::after {{ content: ''; position: absolute; inset: 0; background: url('/allikas/mockups/myra.png'); opacity: .07; mix-blend-mode: overlay; }}
.shade {{ position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 30%, rgba(255,240,210,.08), rgba(0,0,0,.55) 75%); }}
.fascia {{ position: absolute; left: 150px; right: 150px; top: 70px; height: 170px;
          background: radial-gradient(ellipse at 50% -30%, rgba(255,228,175,.16), transparent 62%), linear-gradient(#141414, #0a0a0a);
          border: 2px solid #2b2620; box-shadow: 0 18px 40px rgba(0,0,0,.6), inset 0 0 0 10px #0e0e0e, inset 0 0 0 11px #3a3125; display: grid; place-items: center; }}
.gold {{ background: {GOLD_METAL}; -webkit-mask-size: contain; -webkit-mask-repeat: no-repeat; -webkit-mask-position: center; }}
.fascia .gold {{ width: 520px; height: 120px; -webkit-mask-image: url('{fascia}'); }}
.door {{ position: absolute; left: 439px; width: 540px; top: 300px; bottom: 120px; background: #121110; padding: 26px;
        box-shadow: 0 0 0 2px #050505, inset 0 0 0 2px #37302a, 0 30px 60px rgba(0,0,0,.6); }}
.side {{ position: absolute; left: 221px; width: 198px; top: 300px; bottom: 120px; background: #121110; padding: 18px;
        box-shadow: 0 0 0 2px #050505, inset 0 0 0 2px #37302a; }}
.glass {{ position: relative; width: 100%; height: 100%; overflow: hidden;
         background: radial-gradient(ellipse at 40% 38%, rgba(255,205,140,.20), transparent 55%),
                     radial-gradient(ellipse at 70% 75%, rgba(255,190,120,.10), transparent 45%),
                     linear-gradient(180deg, #22201d 0%, #141311 60%, #0d0c0b 100%); }}
.glass .blur {{ position: absolute; filter: blur(26px); opacity: .55; }}
.glass::after {{ content: ''; position: absolute; inset: 0;
   background: linear-gradient(112deg, transparent 0 28%, rgba(255,255,255,.07) 30%, transparent 36%, transparent 58%, rgba(255,255,255,.045) 61%, transparent 70%); }}
.door .gold.logo {{ position: absolute; left: 10%; right: 12%; top: 16%; height: 24%; -webkit-mask-image: url('{main}'); filter: drop-shadow(0 1px 0 rgba(0,0,0,.35)); }}
.side .gold.logo {{ position: absolute; left: 13%; right: 13%; top: 10%; bottom: 10%; -webkit-mask-image: url('{strip}'); }}
.handle {{ position: absolute; right: 54px; top: 47%; width: 16px; height: 270px; border-radius: 8px;
          background: linear-gradient(90deg, #6a5433, #d9bd84 45%, #8b6d40 60%, #c7a86f); box-shadow: 4px 6px 12px rgba(0,0,0,.55); }}
.handle::before, .handle::after {{ content: ''; position: absolute; left: -22px; width: 26px; height: 10px; background: #7d6440; }}
.handle::before {{ top: 30px; }} .handle::after {{ bottom: 30px; }}
.step {{ position: absolute; left: 120px; right: 120px; bottom: 70px; height: 50px; background: linear-gradient(#3a3733, #1d1c1a); box-shadow: 0 10px 30px rgba(0,0,0,.6); }}
.ground {{ position: absolute; left: 0; right: 0; bottom: 0; height: 70px; background: linear-gradient(#232220, #121212); }}
.tag {{ position: absolute; right: 26px; bottom: 16px; font: 600 11px/1 'Bodoni Moda'; letter-spacing: .3em; color: rgba(255,255,255,.35); font-variation-settings: 'opsz' 6; }}
</style></head><body>
<div class="shade"></div>
<div class="fascia"><div class="gold"></div></div>
<div class="side"><div class="glass"><div class="gold logo"></div></div></div>
<div class="door"><div class="glass">
  <div class="blur" style="left:12%; top:18%; width:120px; height:220px; background:#5a4630"></div>
  <div class="blur" style="left:58%; top:12%; width:160px; height:120px; background:#7a6040"></div>
  <div class="blur" style="left:30%; top:70%; width:220px; height:90px; background:#3a2e22"></div>
  <div class="gold logo"></div></div><div class="handle"></div></div>
<div class="step"></div><div class="ground"></div>
<div class="tag">NÄIDISKUJUNDUS</div>
</body></html>"""


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for d in DIRECTIONS:
        for name, fn, size in (("veeb", web, (1600, 1000)), ("uks", door, (1200, 1500))):
            path = os.path.join(OUT, f"{d}-{name}.html")
            with open(path, "w") as f:
                f.write(fn(d))
            jobs.append((f"/allikas/mockups/_html/{d}-{name}.html", f"{d}-{name}.jpg", *size))
    with open(os.path.join(OUT, "jobs.txt"), "w") as f:
        for j in jobs:
            f.write("\t".join(map(str, j)) + "\n")
    print(len(jobs), "scenes")


if __name__ == "__main__":
    main()
