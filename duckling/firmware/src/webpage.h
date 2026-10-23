#pragma once
// Phone control page, served from flash.
static const char PAGE[] PROGMEM = R"HTML(<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Duckling</title>
<style>
:root{--y:#f6c945;--o:#f28c28;--bg:#fffaf0;--ink:#3b2f1e}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,sans-serif;background:var(--bg);color:var(--ink);text-align:center}
h1{margin:16px 0 4px}small{opacity:.7}
.pad{display:grid;grid-template-columns:repeat(3,88px);gap:10px;justify-content:center;margin:18px 0}
button{font-size:28px;height:80px;border:0;border-radius:18px;background:var(--y);color:var(--ink);box-shadow:0 4px 0 #c99a1c;touch-action:manipulation}
button:active{transform:translateY(3px);box-shadow:0 1px 0 #c99a1c}
.stop{background:#eee;box-shadow:0 4px 0 #bbb}.fun{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;padding:0 16px}
.fun button{font-size:18px;height:56px;padding:0 18px;background:var(--o);color:#fff;box-shadow:0 4px 0 #b35f12}
details{margin:24px 16px;text-align:left;background:#fff;border-radius:14px;padding:12px 16px}
.j{display:grid;grid-template-columns:1fr auto;gap:6px;align-items:center;margin:10px 0}
input[type=range]{grid-column:1/3;width:100%}
</style></head><body>
<h1>&#x1F986; Duckling</h1><small id="bat">battery: --</small>
<div class="pad">
<span></span><button data-m="forward">&#x2B06;</button><span></span>
<button data-m="left">&#x2B05;</button><button class="stop" data-m="center">&#x25A0;</button><button data-m="right">&#x27A1;</button>
<span></span><button data-m="backward">&#x2B07;</button><span></span>
</div>
<div class="fun">
<button onclick="fetch('/api/quack')">Quack!</button>
<button data-m="waddle">Waddle</button><button data-m="dance">Dance</button><button data-m="look">Look around</button>
</div>
<details><summary><b>Setup &amp; calibration</b></summary>
<p>Tap <b>Centre</b> before fitting the servo horns. Then nudge each slider until the joint is straight, and press <b>Save</b>.
Tick <i>reverse</i> if a joint moves the wrong way when walking.</p>
<div id="joints"></div>
<button style="font-size:18px;height:50px;width:100%" onclick="fetch('/api/save').then(()=>alert('Saved'))">Save</button>
</details>
<script>
const go=m=>fetch('/api/move?m='+m).then(r=>r.json()).then(show);
document.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>go(b.dataset.m));
function show(s){
  document.getElementById('bat').textContent=s.battery_mv>2500?'battery: '+(s.battery_mv/1000).toFixed(2)+' V':'battery: not wired';
  const box=document.getElementById('joints');
  if(box.childElementCount)return;
  s.joints.forEach((j,i)=>{
    const d=document.createElement('div');d.className='j';
    d.innerHTML=`<span>${j.name}: <b id="v${i}">${j.trim}</b></span>
      <label><input type="checkbox" id="r${i}" ${j.reversed?'checked':''}> reverse</label>
      <input type="range" min="-30" max="30" value="${j.trim}" id="s${i}">`;
    box.appendChild(d);
    const send=()=>{document.getElementById('v'+i).textContent=d.querySelector('input[type=range]').value;
      fetch(`/api/trim?j=${i}&v=${document.getElementById('s'+i).value}&r=${document.getElementById('r'+i).checked?1:0}`)};
    d.querySelector('input[type=range]').oninput=send;d.querySelector('input[type=checkbox]').onchange=send;
  });
}
fetch('/api/state').then(r=>r.json()).then(show);
setInterval(()=>fetch('/api/state').then(r=>r.json()).then(s=>show(s)),5000);
</script></body></html>)HTML";
