#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 方法论落地页 server.py 通用骨架（红蓝四段式文本解析版）。
改 SYSTEM_PROMPT + parse 逻辑即可复用到其他方法论。
JSON 版（六分身/调研页）用 response_format={"type":"json_object"}，parse_json 剥离围栏。
"""
import json, os, re, requests
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
# ⚠️ DeepSeek key 必须从 ~/.hermes/.env 读（config.yaml 里的 sk-gaw 是 SiliconFlow 的，不是 DeepSeek）
_env = {}
_env_path = Path.home() / ".hermes" / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            _env[k.strip()] = v.strip()
API_KEY = os.environ.get("DEEPSEEK_API_KEY") or _env.get("DEEPSEEK_API_KEY") or ""
DEEPSEEK_URL = (_env.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/v1").rstrip("/") + "/chat/completions"
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

app = FastAPI(title="方法论落地页")

SYSTEM_PROMPT = """你是「方法论执行引擎」。
【在此填入方法论框架 + 用户铁律：收入打折/区分数据与推断/黑海风险/最小行动单元/语气犀利】
输出格式：【JSON 或 固定四段式】"""


@app.post("/api/analyze")
async def analyze(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "请求格式错误"}, status_code=400)
    idea = (body.get("idea") or "").strip()
    if not idea:
        return JSONResponse({"error": "输入不能为空"}, status_code=400)
    if len(idea) > 800:
        return JSONResponse({"error": "输入太长了"}, status_code=400)
    try:
        resp = requests.post(
            DEEPSEEK_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"我的输入是：{idea}\n\n按方法论输出结论。"},
                ],
                "temperature": 0.6,
                "max_tokens": 3500,
                "response_format": {"type": "json_object"},  # 文本四段式版去掉这行
            },
            timeout=150,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        parsed = parse_json(content)  # JSON 版；四段式版用 parse_sections(content)
        return {"ok": True, "sections": parsed, "idea": idea}
    except requests.exceptions.Timeout:
        return JSONResponse({"error": "分析超时，稍后再试"}, status_code=504)
    except Exception as e:
        return JSONResponse({"error": f"分析服务出错：{str(e)[:200]}"}, status_code=500)


def parse_json(content: str):
    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
        return None


def parse_sections(content: str) -> dict:
    """四段式文本版：按段名切分（红蓝：蓝方提案/红方攻击/数据验证清单/结论）。"""
    markers = ["蓝方提案", "红方攻击", "数据验证清单", "结论"]
    text = re.sub(r"^#{1,6}\s*", "", content, flags=re.M)
    text = re.sub(r"^\*{1,3}\s*", "", text, flags=re.M)
    positions = {m: text.find(m) for m in markers if text.find(m) >= 0}
    if len(positions) < len(markers):
        return {"raw": content}
    ordered = sorted(positions.items(), key=lambda x: x[1])
    result = {}
    for i, (name, start) in enumerate(ordered):
        end = ordered[i + 1][1] if i + 1 < len(ordered) else len(text)
        result[name] = text[start:end].strip()[len(name):].strip(":： \n")
    return result


@app.get("/health")
async def health():
    return {"ok": True, "service": "landing"}


@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "index.html")


app.mount("/images", StaticFiles(directory=BASE_DIR / "images"), name="images")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8920)))
