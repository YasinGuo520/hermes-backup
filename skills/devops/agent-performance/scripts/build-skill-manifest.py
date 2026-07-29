#!/usr/bin/env python3
"""
技能档案清单生成器 — 用于 curator 清理后重建「技能档案库.md」
输出到 Obsidian Vault，由 kb_summary 自动蒸馏到共享记忆层。

用法：python3 ~/.hermes/skills/devops/agent-performance/scripts/build-skill-manifest.py
"""
import subprocess, os, sys
from datetime import datetime

VAULT = os.path.expanduser("~/obsidian-vault/Obsidian Vault/_kb/技能档案库.md")
ARCHIVE = os.path.expanduser("~/.hermes/skills/.archive")
HERMES = "hermes"

def usage():
    r = subprocess.run(f"{HERMES} curator usage 2>&1", shell=True, capture_output=True, text=True, timeout=120)
    skills = []
    for line in r.stdout.split('\n'):
        p = line.strip().split()
        if len(p) >= 7:
            try:
                skills.append(dict(name=p[0], origin=p[1], activity=int(p[5]), last=' '.join(p[6:])))
            except: pass
    return skills

def archived():
    if not os.path.isdir(ARCHIVE): return []
    return sorted(d for d in os.listdir(ARCHIVE) if os.path.isdir(os.path.join(ARCHIVE, d)))

CAT = [
    ('commerce', ['douyin-livestream','ecommerce','traffic-acquisition','productization','content-risk','monetization-case','domestic-video','cover-image','saas-productization']),
    ('content', ['video-maker','video-production','video-content','short-drama','llm-video','chaoke-i2v','edit-video','humanizer','xiaohuangben','xhs','youtube','scheduled-content','aliang-shortvideo','aliang-picturebook','aliang-kids','aliang-product','aliang-podcast','aliang-bailian-voice','aliang-bailian']),
    ('jianying', ['jianying']),
    ('audio', ['voice-input','songwrit','heartmula','gif']),
    ('visual', ['ux-pro-max','frontend-design','immersive','creative-page','celebration','html-game','html-canvas','claude-design','sketch','p5js','pixel-art','architecture','ascii','baoyu','excalidraw','pretext','visual-component','popular-web','mind-map','design-inspiration','design-md']),
    ('stock', ['a-share-stock','a-share-market','pnl']),
    ('research', ['niche-market','china-market','china-industry','enterprise-agent','deep-research']),
    ('dev', ['spike','debugpy','node-inspect','test-driven','simplify','requesting-code','systematic-debugging','claude-mem','skill-creator','hermes-agent-skill','subagent-project','find-skills','install-github','superpowers','understand-anything','graphify','deer-flow','code-review']),
    ('agent', ['agent-performance','project-four-persona','project-recommendation','personal-knowledge','coze-template','autonomous','ai-saas']),
    ('scraper', ['web-scraping','scrapling','playwright']),
    ('ops', ['server-service','weixin-ilink','feishu-lark','qq-bot','macos-backup','server-migration','hermes-cron','hermes-desktop']),
    ('doc', ['powerpoint','pptx','docx','xlsx','pdf','nano-pdf','markitdown','ocr','notion','google-workspace','airtable','maps','translate','markdown-to-html','content-polish','post-to','imessage','apple-notes','apple-reminders','findmy','note']),
    ('media', ['blender','comfyui','touchdesigner','manim','songwriting']),
    ('hermes', ['hermes-agent','computer-use']),
]

CAT_NAMES = {
    'commerce':'📊 电商实战','content':'🎬 内容创作','jianying':'🎬 剪映','audio':'🎵 音频',
    'visual':'🎨 视觉 & 前端','stock':'📈 量化 & 股票','research':'🔬 调研','dev':'🔧 开发',
    'agent':'🤖 AI & Agent','scraper':'🕸️ 爬虫','ops':'⚙️ 运维','doc':'📄 文档 & 办公',
    'media':'🎬 媒体','hermes':'🔧 Hermes核心','other':'📦 其他',
}

def cat_of(name):
    for c, kws in CAT:
        for kw in kws:
            if kw in name: return c
    return 'other'

def build(skills, archive_list):
    agent = [s for s in skills if s['origin']=='agent']
    bundled = [s for s in skills if s['origin'] in ('bundled','hub')]
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = [f"# 🛠️ Hermes 技能档案库  \n"]
    lines.append(f"> **{len(agent)+len(bundled)} 技能**（agent={len(agent)}, bundled={len(bundled)}, 归档={len(archive_list)}）  ")
    lines.append(f"> 更新：{now}  \n")
    lines.append("---\n")
    lines.append("**使用：** 说技能名加载 | 说「恢复XX」从归档还原  \n")
    lines.append("---\n")

    groups = {}
    for s in agent:
        groups.setdefault(cat_of(s['name']), []).append(s)

    for g in sorted(groups):
        label = CAT_NAMES.get(g, g)
        items = sorted(groups[g], key=lambda x: -x['activity'])
        lines.append(f"### {label} ({len(items)})  \n")
        lines.append("| 技能 | 活跃 | 最后 |\n|------|:----:|------|\n")
        for s in items:
            lines.append(f"| `{s['name']}` | {s['activity']} | {s['last']} |\n")
        lines.append("")

    if archive_list:
        lines.append("---\n## 🗄️ 归档技能\n")
        lines.append("| 技能 | 恢复 |\n|------|------|\n")
        for s in archive_list:
            lines.append(f"| `{s}` | `hermes curator restore {s}` |\n")
        lines.append("")

    lines.append(f"---\n> {now}\n")
    return ''.join(lines)

if __name__ == '__main__':
    s = usage()
    a = archived()
    m = build(s, a)
    os.makedirs(os.path.dirname(VAULT), exist_ok=True)
    with open(VAULT, 'w', encoding='utf-8') as f:
        f.write(m)
    agent = len([x for x in s if x['origin']=='agent'])
    bundled = len([x for x in s if x['origin'] in ('bundled','hub')])
    print(f"✅ {VAULT}")
    print(f"   {agent} agent + {bundled} bundled + {len(a)} archived = {agent+bundled+len(a)} total")
