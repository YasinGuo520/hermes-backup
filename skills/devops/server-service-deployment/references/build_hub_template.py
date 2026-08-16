#!/usr/bin/env python3
"""Hermes项目导航中心 — 列出所有HTML项目，一键跳转"""

# ─── 项目列表（以后加新项目就在这里加一行） ───
PROJECTS = [
    {
        "port": 8900,
        "name": "🧰 方法论工具箱",
        "desc": "一人公司的私人工具库 · 130工具 · 7大类。搜索过滤、分类筛选、点击展开详情。",
        "icon": "🧰",
        "color": "#6c5ce7",
        "tags": ["工具库", "方法论", "全部"]
    },
    {
        "port": 8899,
        "name": "🎂 莹莹生日",
        "desc": "郭泽莹13岁生日沉浸式互动页面。星空粒子、动漫化头像、吧唧彩花、礼物盒气球。",
        "icon": "🎂",
        "color": "#f472b6",
        "tags": ["生日", "互动", "沉浸式"]
    },
    {
        "port": 8894,
        "name": "👤 个人简历",
        "desc": "Yasin个人简历和作品集。含电商AI-Agent七套体系技术拆解。",
        "icon": "👤",
        "color": "#10b981",
        "tags": ["简历", "作品集", "个人"]
    },
]

# ─── 外部链接（不在本服务器上，但经常用的） ───
EXTERNAL_LINKS = [
    {"name": "🔗 服小助AI客服", "url": "http://43.138.221.174:8000", "desc": "电商AI客服SaaS · 腾讯云轻量服务器"},
    {"name": "🔗 Kronos看板", "url": "http://43.138.221.174:8080", "desc": "量化选股系统WebUI看板"},
]


def build():
    import os

    # Build project cards
    cards = []
    for p in PROJECTS:
        tags_html = ''.join(f'<span class="tag">{t}</span>' for t in p["tags"])
        color = p["color"]
        card = f'''<a class="card" href="http://43.138.221.174:{p["port"]}" target="_blank">
      <div class="card-icon" style="background:{color}20">{p["icon"]}</div>
      <div class="card-body">
        <div class="card-name">{p["name"]}</div>
        <div class="card-desc">{p["desc"]}</div>
        <div class="card-meta">
          <span class="port-badge" style="color:{color}">{p["port"]}</span>
          {tags_html}
        </div>
      </div>
      <div class="card-arrow">→</div>
    </a>'''
        cards.append(card)

    # Build external links
    ext_cards = []
    for l in EXTERNAL_LINKS:
        ext_cards.append(f'''<a class="external-link" href="{l["url"]}" target="_blank">
      <div class="info">
        <div class="name">{l["name"]}</div>
        <div class="desc">{l["desc"]}</div>
      </div>
      <span class="url-badge">→</span>
    </a>''')

    total = len(PROJECTS) + len(EXTERNAL_LINKS)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Yasin · 项目导航</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: 'Inter', -apple-system, sans-serif;
    background: #0a0a0f;
    color: #e0e0e0;
    min-height: 100vh;
    overflow-x: hidden;
  }}
  #bg-canvas {{
    position: fixed; top:0; left:0; width:100%; height:100%;
    z-index:0; pointer-events:none;
  }}
  .container {{
    position:relative; z-index:1;
    max-width:1000px; margin:0 auto; padding:40px 24px;
  }}
  .header {{ text-align:center; padding:32px 0 40px; }}
  .header h1 {{
    font-size:2.4rem; font-weight:700;
    background:linear-gradient(135deg,#a78bfa,#6c5ce7,#3b82f6);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:8px;
  }}
  .header p {{ color:#666; font-size:0.95rem; }}
  .header .stats {{ margin-top:8px; color:#555; font-size:0.85rem; }}
  .header .stats span {{ color:#a78bfa; font-weight:600; }}
  .section-title {{
    font-size:1.1rem; font-weight:600; margin:32px 0 16px;
    color:#888; letter-spacing:0.5px;
  }}
  .project-grid {{ display:flex; flex-direction:column; gap:12px; }}
  .card {{
    display:flex; align-items:center; gap:16px;
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:14px;
    padding:16px 20px;
    cursor:pointer;
    transition:all 0.25s ease;
    text-decoration:none;
    color:inherit;
    position:relative;
    overflow:hidden;
  }}
  .card::before {{
    content:''; position:absolute; left:0; top:0; bottom:0;
    width:3px;
    background:var(--accent,#6c5ce7);
    opacity:0;
    transition:opacity 0.25s;
  }}
  .card:hover {{
    border-color:rgba(108,92,231,0.3);
    background:rgba(255,255,255,0.06);
    transform:translateX(4px);
  }}
  .card:hover::before {{ opacity:1; }}
  .card-icon {{
    width:48px; height:48px; border-radius:12px;
    display:flex; align-items:center; justify-content:center;
    font-size:1.5rem;
    flex-shrink:0;
  }}
  .card-body {{ flex:1; min-width:0; }}
  .card-name {{
    font-size:1.05rem; font-weight:600; margin-bottom:4px;
    color:#e0e0e0;
  }}
  .card-desc {{ font-size:0.85rem; color:#777; line-height:1.5; }}
  .card-meta {{
    display:flex; align-items:center; gap:10px; margin-top:8px;
  }}
  .port-badge {{
    display:inline-block;
    background:rgba(255,255,255,0.06);
    padding:2px 8px; border-radius:6px;
    font-size:0.75rem; font-family:'JetBrains Mono',monospace;
  }}
  .tag {{
    display:inline-block;
    background:rgba(255,255,255,0.04);
    padding:2px 8px; border-radius:6px;
    font-size:0.72rem; color:#555;
  }}
  .card-arrow {{
    font-size:1.2rem; color:#333;
    flex-shrink:0; transition:transform 0.2s;
  }}
  .card:hover .card-arrow {{ transform:translateX(4px); color:#a78bfa; }}
  .external-section {{ margin-top:24px; }}
  .external-link {{
    display:flex; align-items:center; gap:14px;
    padding:14px 20px;
    background:rgba(255,255,255,0.02);
    border:1px solid rgba(255,255,255,0.05);
    border-radius:12px;
    margin-bottom:8px;
    transition:all 0.2s;
    text-decoration:none; color:inherit;
  }}
  .external-link:hover {{
    background:rgba(255,255,255,0.05);
    border-color:rgba(59,130,246,0.3);
  }}
  .external-link .info {{ flex:1; }}
  .external-link .name {{ font-weight:500; font-size:0.95rem; }}
  .external-link .desc {{ font-size:0.8rem; color:#666; margin-top:2px; }}
  .external-link .url-badge {{
    font-size:0.75rem; color:#3b82f6;
    font-family:'JetBrains Mono',monospace;
  }}
  .footer {{
    text-align:center; padding:48px 0 24px;
    color:#333; font-size:0.8rem;
  }}
  @media (max-width:600px) {{
    .card {{ flex-wrap:wrap; gap:10px; }}
    .card-body {{ width:100%; }}
    .header h1 {{ font-size:1.6rem; }}
  }}
</style>
</head>
<body>
<canvas id="bg-canvas"></canvas>
<div class="container">
  <div class="header">
    <h1>🚀 Yasin · 项目导航</h1>
    <p>Hermes 所有HTML项目 · 一键直达</p>
    <div class="stats"><span>{total}</span> 个项目正在运行</div>
  </div>

  <div class="section-title">📌 HTML 项目</div>
  <div class="project-grid">
    {cards}
  </div>

  <div class="section-title">🔗 外部服务</div>
  <div class="external-section">
    {ext_cards}
  </div>

  <div class="footer">
    新增项目 → 编辑 hermes-hub/build_hub.py 的 PROJECTS 列表添加一行即可
  </div>
</div>

<script>
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
let particles = [];
function resize() {{ canvas.width = window.innerWidth; canvas.height = document.body.scrollHeight; }}
window.addEventListener('resize', resize); resize();

for(let i=0;i<40;i++) {{
  particles.push({{
    x: Math.random()*canvas.width, y: Math.random()*canvas.height,
    vx: (Math.random()-0.5)*0.2, vy: (Math.random()-0.5)*0.2,
    r: Math.random()*2+0.5, a: Math.random()*0.2+0.05
  }});
}}
function animate() {{
  ctx.clearRect(0,0,canvas.width,canvas.height);
  for(const p of particles) {{
    p.x+=p.vx; p.y+=p.vy;
    if(p.x<0) p.x=canvas.width; if(p.x>canvas.width) p.x=0;
    if(p.y<0) p.y=canvas.height; if(p.y>canvas.height) p.y=0;
    ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx.fillStyle='rgba(108,92,231,'+(p.a)+')';
    ctx.fill();
  }}
  for(let i=0;i<particles.length;i++) {{
    for(let j=i+1;j<particles.length;j++) {{
      const dx=particles[i].x-particles[j].x, dy=particles[i].y-particles[j].y;
      const d=Math.sqrt(dx*dx+dy*dy);
      if(d<120) {{
        ctx.beginPath(); ctx.moveTo(particles[i].x,particles[i].y);
        ctx.lineTo(particles[j].x,particles[j].y);
        ctx.strokeStyle='rgba(108,92,231,'+((1-d/120)*0.06)+')';
        ctx.lineWidth=0.5; ctx.stroke();
      }}
    }}
  }}
  requestAnimationFrame(animate);
}}
animate();
</script>
</body>
</html>'''

    out = os.path.expanduser("~/Desktop/hermes/hermes-hub/index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 导航页生成 → {out}")
    print(f"   项目: {len(PROJECTS)} · 外部服务: {len(EXTERNAL_LINKS)} · 总计: {total}")

if __name__ == "__main__":
    build()
