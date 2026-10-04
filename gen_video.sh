#!/bin/bash
THEME=$1
EMOJI1=$2
EMOJI2=$3
EMOJI3=$4
TITLE=$5

mkdir -p $THEME/frames
cd $THEME

cat > index.html <<EOF
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta data-canvas-width="1080" data-canvas-height="1920">
<style>*{margin:0;padding:0;box-sizing:border-box}body{width:1080px;height:1920px;background:linear-gradient(180deg,#87CEEB 0%,#E0F6FF 50%,#90EE90 100%);display:flex;align-items:center;justify-content:center;font-family:Arial}.container{width:100%;height:100%;position:relative}.scene{position:absolute;width:100%;height:100%;display:flex;align-items:center;justify-content:center;flex-direction:column;opacity:0;transition:opacity 1s}.scene.active{opacity:1}.animals{display:flex;gap:150px;justify-content:center}.animal{font-size:150px}.title{font-size:72px;font-weight:bold;color:white;text-shadow:4px 4px 8px rgba(0,0,0,0.3)}</style>
</head>
<body>
<div class="container" data-composition-id="vid" data-duration="60">
<div class="scene active" id="s0"><div style="font-size:200px">$EMOJI1</div><div class="title">¡Bienvenida!</div></div>
<div class="scene" id="s1"><div class="animal">$EMOJI1</div><div class="title">¡Primero!</div></div>
<div class="scene" id="s2"><div class="animal">$EMOJI2</div><div class="title">¡Segundo!</div></div>
<div class="scene" id="s3"><div class="animal">$EMOJI3</div><div class="title">¡Tercero!</div></div>
<div class="scene" id="s4"><div class="animals"><div class="animal">$EMOJI1</div><div class="animal">$EMOJI2</div><div class="animal">$EMOJI3</div></div><div class="title">¡Todos Juntos!</div></div>
<div class="scene" id="s5"><div class="animals"><div class="animal">$EMOJI1</div><div class="animal">$EMOJI2</div><div class="animal">$EMOJI3</div></div><div class="title">$TITLE</div><div style="font-size:54px;color:#FFD700;margin-top:20px">❤️ FIN ❤️</div></div>
</div>
<script>
const scenes=[{id:'s0',start:0,duration:5},{id:'s1',start:5,duration:7},{id:'s2',start:12,duration:8},{id:'s3',start:20,duration:8},{id:'s4',start:28,duration:17},{id:'s5',start:45,duration:15}];
let t=0;function a(){scenes.forEach(s=>{const e=document.getElementById(s.id);t>=s.start&&t<s.start+s.duration?e.classList.add('active'):e.classList.remove('active')});t+=0.033;t<60&&requestAnimationFrame(a)}a();
</script></body></html>
EOF

# Render frames
node -e "
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://$(pwd)/index.html',{waitUntil:'load'});
for(let i=0;i<60;i++){
  await p.evaluate(t=>{window.currentTime=t},i);
  await p.waitForTimeout(50);
  await p.screenshot({path:\`frames/f\${String(i).padStart(6,'0')}.jpg\`});
  if((i+1)%15===0)console.log('.');
}
await b.close();
console.log('✓');
})();
" 2>&1 | grep -E "✓|Error" &

wait
cd ..
