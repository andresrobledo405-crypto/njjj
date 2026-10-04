#!/usr/bin/env python3
"""Genera promo (vertical 1080x1920) y promo-landscape (1920x1080) desde una sola plantilla."""
import os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "promo")
S = [0, 5.2, 12.0, 16.2]          # inicio de cada escena
D = [5.2, 6.8, 4.2, 3.8]          # duración de cada escena
TOTAL = 20
VOICE = [0.3, 5.5, 12.3, 16.5]    # inicio de cada clip de voz

LAYOUTS = {
  "portrait": dict(w=1080, h=1920, pad="0 96px", h1=150, h2=88, sub=44, pill=52, pillpad="44px 52px", bub=48,
                   bubmax=800, cta=64, extra=""),
  "landscape": dict(w=1920, h=1080, pad="0 160px", h1=132, h2=76, sub=40, pill=44, pillpad="26px 44px", bub=40,
                    bubmax=1000, cta=52,
                    extra=".pills{display:grid;grid-template-columns:1fr 1fr;gap:24px}.pill{margin-bottom:0!important}"
                          "h2{margin-bottom:48px!important}.cta{margin-top:40px!important}"),
}

def page(L):
    return f'''<!doctype html>
<html lang="es" data-resolution="{ 'portrait' if L['w']<L['h'] else 'landscape' }">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={L['w']}, height={L['h']}" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {L['w']}px; height: {L['h']}px; overflow: hidden; background: #121110; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden;
        font-family: system-ui, -apple-system, "Segoe UI", sans-serif; color: #f3f1ed;
        background: radial-gradient(900px 900px at 80% 10%, #1d2a6b 0%, #121110 60%); }}
      .scene {{ position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; padding: {L['pad']}; opacity: 0; }}
      h1 {{ font-size: {L['h1']}px; line-height: 1; font-weight: 800; letter-spacing: -0.045em; }}
      h1 span {{ color: #6b8cff; }}
      h2 {{ font-size: {L['h2']}px; line-height: 1.05; font-weight: 700; letter-spacing: -0.04em; margin-bottom: 72px; }}
      .sub {{ margin-top: 36px; font-size: {L['sub']}px; color: #9a958d; letter-spacing: -0.01em; }}
      .pill {{ display: block; font-size: {L['pill']}px; font-weight: 600; padding: {L['pillpad']}; margin-bottom: 28px; border-radius: 36px; background: #1f1d1b; border: 2px solid #2c2a27; }}
      .pill b {{ color: #6b8cff; margin-right: 24px; }}
      .bubble {{ max-width: {L['bubmax']}px; font-size: {L['bub']}px; line-height: 1.35; padding: 32px 44px; border-radius: 52px; margin-bottom: 28px; }}
      .user {{ align-self: flex-end; background: #6b8cff; color: #fff; border-bottom-right-radius: 16px; }}
      .bot {{ align-self: flex-start; background: #1f1d1b; border-bottom-left-radius: 16px; }}
      .cta {{ font-size: {L['cta']}px; font-weight: 700; padding: 40px 72px; border-radius: 999px; background: #6b8cff; color: #fff; align-self: flex-start; margin-top: 64px; letter-spacing: -0.02em; }}
      {L['extra']}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{L['w']}" data-height="{L['h']}">
      <div class="scene" id="s1">
        <h1 id="t1">IA en su <span>teléfono</span></h1>
        <p class="sub" id="t1s">Cuatro formas. Un solo proyecto.</p>
      </div>
      <div class="scene" id="s2">
        <h2 id="t2">Elija su camino</h2>
        <div class="pills">
          <div class="pill p"><b>1</b>App móvil con Claude</div>
          <div class="pill p"><b>2</b>IA local sin internet</div>
          <div class="pill p"><b>3</b>Asistentes ya hechos</div>
          <div class="pill p"><b>4</b>SMS y llamadas</div>
        </div>
      </div>
      <div class="scene" id="s3">
        <h2 id="t3">Pregunte. Envíe una foto.</h2>
        <div class="bubble user" id="b1">¿Qué planta es esta?</div>
        <div class="bubble bot" id="b2">Es un potos. Necesita luz indirecta y poca agua.</div>
      </div>
      <div class="scene" id="s4">
        <h1 id="t4">Pruébela<span>.</span></h1>
        <p class="sub">Servidor + app Expo + Twilio</p>
        <div class="cta" id="cta">Empezar</div>
      </div>
      <audio id="music" src="assets/music.wav" data-start="0" data-duration="{TOTAL}" data-track-index="20" data-volume="0.35"></audio>
      {''.join(f'<audio id="voice{i+1}" src="assets/v{i+1}.wav" data-start="{VOICE[i]}" data-track-index="{21+i}" data-volume="1"></audio>' for i in range(4))}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const out = "expo.out";
      const S = {S}, D = {D};
      ["#s1", "#s2", "#s3", "#s4"].forEach((id, i) => {{
        tl.fromTo(id, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, S[i]);
        if (i < 3) tl.to(id, {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, S[i] + D[i] - 0.3);
      }});
      const rise = (sel, t, extra = {{}}) => tl.fromTo(sel, {{ y: 30, opacity: 0, ...extra.from }}, {{ y: 0, opacity: 1, duration: 0.7, ease: out, ...extra.to, stagger: extra.stagger }}, t);
      rise("#t1", S[0] + 0.1); rise("#t1s", S[0] + 0.7);
      rise("#t2", S[1] + 0.1);
      rise(".p", S[1] + 0.6, {{ from: {{ scale: 0.96 }}, to: {{ scale: 1 }}, stagger: 0.9 }});
      rise("#t3", S[2] + 0.1);
      rise("#b1", S[2] + 0.8, {{ from: {{ scale: 0.96 }}, to: {{ scale: 1 }} }});
      rise("#b2", S[2] + 1.9, {{ from: {{ scale: 0.96 }}, to: {{ scale: 1 }} }});
      rise("#t4", S[3] + 0.1); rise("#cta", S[3] + 0.9, {{ from: {{ scale: 0.96 }}, to: {{ scale: 1 }} }});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
'''

for name, key in (("promo", "portrait"), ("promo-landscape", "landscape")):
    dst = os.path.join(HERE, name)
    if name != "promo":
        shutil.copytree(SRC, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("node_modules", "index.html"))
    open(os.path.join(dst, "index.html"), "w").write(page(LAYOUTS[key]))
    print("wrote", name)
