#!/usr/bin/env python3
"""Seedance 逐镜图生视频生成器（火山方舟 ARK）
用法:
  python3 seedance_gen.py --image product.jpg --storyboard storyboard.json \
      --model doubao-seedance-1-0-pro-fast-251015 --outdir video_shots

读取 storyboard.json 的每镜 image_prompt 作为运镜/动作 prompt，
逐镜串行调 ARK contents/generations/tasks 生成视频并下载。
"""
import argparse, json, os, sys, time, base64, urllib.request, urllib.error

API_BASE = "https://ark.cn-beijing.volces.com/api/v3"

def load_key():
    """从 backend/.env 读 ARK_API_KEY"""
    env_path = os.path.expanduser("~/backend/.env")
    if os.path.exists(env_path):
        for line in open(env_path):
            line = line.strip()
            if line.startswith("ARK_API_KEY="):
                return line.split("=", 1)[1].strip()
    # 环境变量兜底
    key = os.environ.get("ARK_API_KEY")
    if key:
        return key
    sys.exit("❌ 找不到 ARK_API_KEY，检查 ~/backend/.env 或环境变量")

def api_request(method, path, key, payload=None):
    url = API_BASE + path
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    data = json.dumps(payload).encode() if payload else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        sys.exit(f"❌ API {e.code}: {body}")

def submit_task(key, model, image_b64, prompt, resolution="720p", duration=5):
    """提交图生视频任务，返回 task_id"""
    payload = {
        "model": model,
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
        ],
        "resolution": resolution,
        "duration": duration,
    }
    result = api_request("POST", "/contents/generations/tasks", key, payload)
    task_id = result.get("id")
    if not task_id:
        sys.exit(f"❌ 提交失败: {result}")
    return task_id

def poll_task(key, task_id, timeout_s=600, interval=15):
    """轮询任务直到 succeeded/failed"""
    start = time.time()
    while time.time() - start < timeout_s:
        result = api_request("GET", f"/contents/generations/tasks/{task_id}", key)
        status = result.get("status")
        if status == "succeeded":
            return result
        if status in ("failed", "cancelled", "expired"):
            sys.exit(f"❌ 任务{status}: {result.get('error')}")
        print(f"  ⏳ {task_id} {status}... 已等{int(time.time()-start)}s")
        time.sleep(interval)
    sys.exit(f"❌ 任务超时 {timeout_s}s: {task_id}")

def download(url, out_path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = resp.read()
    with open(out_path, "wb") as f:
        f.write(data)
    return len(data)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="产品图路径")
    ap.add_argument("--storyboard", required=True, help="storyboard.json")
    ap.add_argument("--model", default="doubao-seedance-1-0-pro-fast-251015")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--resolution", default="720p", choices=["480p", "720p", "1080p"])
    ap.add_argument("--duration", type=int, default=5)
    args = ap.parse_args()

    key = load_key()
    os.makedirs(args.outdir, exist_ok=True)

    with open(args.image, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    with open(args.storyboard) as f:
        sb = json.load(f)

    shots = sb.get("shots", [])
    print(f"📋 共 {len(shots)} 镜，模型 {args.model}，{args.resolution}")

    for i, shot in enumerate(shots, 1):
        prompt = shot.get("image_prompt") or shot.get("prompt") or shot.get("camera", "")
        if not prompt:
            print(f"  ⚠️ 第{i}镜无 prompt，跳过")
            continue
        out_path = os.path.join(args.outdir, f"shot_{i:02d}.mp4")
        if os.path.exists(out_path):
            print(f"  ⏭️ 第{i}镜已存在，跳过: {out_path}")
            continue

        print(f"🎬 第{i}镜: {prompt[:80]}...")
        task_id = submit_task(key, args.model, image_b64, prompt, args.resolution, args.duration)
        print(f"  已提交: {task_id}")
        result = poll_task(key, task_id)
        video_url = result["content"]["video_url"]
        size = download(video_url, out_path)
        print(f"  ✅ 第{i}镜完成: {out_path} ({size/1024/1024:.1f}MB)")

    print("🎉 全部镜头生成完毕")

if __name__ == "__main__":
    main()
