#!/usr/bin/env python3
"""混元3D 图生3D：提交任务 → 轮询 → 下载模型（OBJ zip / GLB）
用法：
  export TENCENT_SECRET_ID=AKID...
  export TENCENT_SECRET_KEY=...
  python hunyuan3d.py --image_url "http://IP:PORT/img.png" --out model_raw.zip --poll_interval 15
"""
import json, os, sys, time, subprocess, argparse
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ai3d.v20250513 import ai3d_client, models

SECRET_ID = os.environ.get("TENCENT_SECRET_ID", "")
SECRET_KEY = os.environ.get("TENCENT_SECRET_KEY", "")

def get_client():
    cred = credential.Credential(SECRET_ID, SECRET_KEY)
    hp = HttpProfile(endpoint="ai3d.tencentcloudapi.com")
    hp.reqTimeout = 30
    cp = ClientProfile(httpProfile=hp)
    return ai3d_client.Ai3dClient(cred, "ap-guangzhou", cp)

def submit(client, image_url):
    req = models.SubmitHunyuanTo3DRapidJobRequest()
    req.ImageUrl = image_url
    resp = client.SubmitHunyuanTo3DRapidJob(req)
    return json.loads(resp.to_json_string())

def query(client, job_id):
    req = models.QueryHunyuanTo3DRapidJobRequest()
    req.JobId = job_id
    resp = client.QueryHunyuanTo3DRapidJob(req)
    return json.loads(resp.to_json_string())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image_url", required=True, help="2D立绘公网URL（纯色/纯黑背景最佳）")
    ap.add_argument("--out", default="model_raw.zip", help="输出文件路径（zip 或 glb）")
    ap.add_argument("--poll_interval", type=int, default=15)
    ap.add_argument("--max_wait", type=int, default=900)
    args = ap.parse_args()

    client = get_client()
    print("提交任务...", flush=True)
    sub = submit(client, args.image_url)
    print("提交响应:", json.dumps(sub, ensure_ascii=False), flush=True)
    job_id = sub.get("JobId")
    if not job_id:
        sys.exit("没有 JobId，失败")

    print("轮询任务:", job_id, flush=True)
    start = time.time()
    result = None
    while time.time() - start < args.max_wait:
        try:
            resp = query(client, job_id)
        except Exception as e:
            print(f"[{int(time.time()-start)}s] 查询异常(重试): {str(e)[:120]}", flush=True)
            time.sleep(args.poll_interval)
            continue
        status = resp.get("Status", resp.get("StatusCode", ""))
        print(f"[{int(time.time()-start)}s] Status: {status}", flush=True)
        if status in ("DONE", "SUCCEED", "SUCCESS", 2, "2"):
            result = resp
            break
        if status in ("FAIL", "FAILED", 3, "3"):
            print("任务失败:", json.dumps(resp, ensure_ascii=False, indent=2), flush=True)
            sys.exit(1)
        time.sleep(args.poll_interval)

    if not result:
        sys.exit("超时未完成")

    # 找模型URL：优先 GLB，其次 OBJ zip
    model_url = None
    for f in result.get("ResultFile3Ds", []):
        if f.get("Type") == "GLB":
            model_url = f.get("Url"); break
    if not model_url:
        for f in result.get("ResultFile3Ds", []):
            if f.get("Type") == "OBJ":
                model_url = f.get("Url"); break

    if not model_url:
        print("没找到模型URL，完整响应:", json.dumps(result, ensure_ascii=False, indent=2), flush=True)
        sys.exit(1)

    print("下载模型...", flush=True)
    subprocess.run(["curl", "-sL", "-o", args.out, model_url], check=True, timeout=300)
    size = os.path.getsize(args.out)
    if size > 1000:
        print(f"✅ 模型已保存: {args.out} ({size} bytes)", flush=True)
    else:
        print("⚠️ 下载文件太小，可能失败", flush=True)

if __name__ == "__main__":
    main()
