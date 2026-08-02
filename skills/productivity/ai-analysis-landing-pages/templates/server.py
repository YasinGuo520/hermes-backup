#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI分析落地页后端脚手架 — 静态页面 + POST /api/analyze → DeepSeek JSON"""
import json, os, re, requests
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
# DeepSeek key 在 ~/.hermes/.env（config.yaml 的 sk- 是 SiliconFlow 的，调 DeepSeek 会 401）
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

app = FastAPI(title="AI分析落地页")

# 方法论提示词：内置 Yasin 铁律（收入打折/数据诚实/黑海风险/最小行动单元/语气犀利）
SYSTEM_PROMPT = """(填你的方法论框架提示词)
铁律：
1. 收入预测打折扣，不确定标「需验证」
2. 区分「有数据支撑的结论」和「推断」，推断标注
3. 空市场可能黑海不装蓝海
4. 结论给「今天就能做的最小行动单元」
5. 语气直接犀利，不鸡汤
输出必须是严格 JSON（不要输出 JSON 之外的内容，不要 markdown 代码块）：
{...}"""

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
        return JSONResponse({"error": "输入太长，精简到800字以内"}, status_code=400)
    try:
        resp = requests.post(
            DEEPSEEK_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"我的想法是：{idea}"},
                ],
                "temperature": 0.6,
                "max_tokens": 3000,  # 多段/六分身用 4500
                "response_format": {"type": "json_object"},
            },
            timeout=150,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return {"ok": True, "sections": parse_json(content), "idea": idea}
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

@app.get("/health")
async def health():
    return {"ok": True, "service": "ai-landing"}

@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "index.html")

# 启动前必须 mkdir -p static images，否则 mount 直接 RuntimeError
app.mount("/images", StaticFiles(directory=BASE_DIR / "images"), name="images")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8920)))
