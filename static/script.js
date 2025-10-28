async function callStatus(){
  const r = await fetch('/api/status');
  const j = await r.json();
  if(j.ok) renderAll(j);
}
async function callSubmit(text){
  try{
    const r = await fetch('/api/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
    const j = await r.json();
    if(!j.ok){ alert(j.msg||'提交失敗'); return; }
    renderAll(j);
  }catch(e){ alert('連線失敗'); }
}
async function callClear(){
  const r = await fetch('/api/clear',{method:'POST'});
  const j = await r.json();
  if(j.ok) renderAll(j);
}
function renderAll(j){
  const s=j.stats||{b:0,p:0,t:0,total:0};
  document.getElementById('stat-b').textContent=s.b??0;
  document.getElementById('stat-p').textContent=s.p??0;
  document.getElementById('stat-t').textContent=s.t??0;
  document.getElementById('stat-total').textContent=s.total??0;

  const box=document.getElementById('route'); if(box){ box.innerHTML=''; (j.route||[]).forEach(x=>{const d=document.createElement('div'); d.className='pill'; d.textContent=x; box.appendChild(d);}); }

  const sug=j.suggestion||{};
  const label=sug.choice==='B'?'莊':sug.choice==='P'?'閒':sug.choice==='T'?'和':'—';
  const conf=Math.round(((sug.confidence||0)*100));
  const advice=document.getElementById('advice'); if(advice){ advice.textContent=`下一局建議：${label}${conf?`（信心 ${conf}%）`:''}`; }

  const stake=j.stake||{};
  const stakeBox=document.getElementById('stake'); if(stakeBox){ stakeBox.textContent = `配注建議：${stake.name||'—'}${stake.step?` 第 ${stake.step} 步`:''}，下 ${stake.units||1} 單位`; }

  const pnl=document.getElementById('pnl'); if(pnl){ pnl.textContent = j.pnl ?? 0; }
}
window.addEventListener('DOMContentLoaded', ()=>{
  const b=document.getElementById('btn-b'); if(b) b.onclick=()=>callSubmit('B');
  const p=document.getElementById('btn-p'); if(p) p.onclick=()=>callSubmit('P');
  const t=document.getElementById('btn-t'); if(t) t.onclick=()=>callSubmit('T');
  const s=document.getElementById('btn-send'); if(s) s.onclick=()=>{const v=document.getElementById('txt').value.trim(); if(!v) return; callSubmit(v); document.getElementById('txt').value='';};
  const c=document.getElementById('btn-clear'); if(c) c.onclick=callClear;
  callStatus();
});
