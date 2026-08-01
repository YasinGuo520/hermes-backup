#!/usr/bin/env python3
"""混元3D 图生3D：提交任务 → 轮询 → 下载OBJ zip。已跑通（2026-08）。

用法:
  export TENCENT_SECRET_ID=... TENCENT_SECRET_KEY=...
  python hunyuan3d.py --image_url "http://IP:PORT/img.png" --out model_raw.zip

依赖: ./venv/bin/pip install --index-url https://mirrors.aliyun.com/pypi/simple/ \
        --trusted-host mirrors.aliyun.com tencentcloud-sdk-python

注意:
  - SDK 模块是 ai3d.v20250513（不是 v20241218）
  - 必须先开通服务并去控制台领取免费积分包，否则报 ResourceInsufficient
  - 轮询偶发 Connection reset，try/except 继续即可
  - 极速版返回 OBJ zip（不是 GLB），解压后需 obj2gltf 转 GLB
"""
import json, os, sys, time, subprocess, argparse
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ai3d.v20250513 import ai3d_client, models

SECRET_ID = os.environ.get("TENCENT_SECRET_ID", "")
SECRET_KEY = os.environ.get("TENCENT_SECRET_KEY", "")

def get_client():
    if not SECRET_ID or not SECRET_KEY:
        # 尝试同目录 .env
        envp = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(envp):
            for line in open(envp):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()
    cred = credential.Credential(
        os.environ.get("TENCENT_SECRET_ID", ""),
        os.environ.get("TENCENT_SECRET_KEY", ""))
    hp = HttpProfile(endpoint="ai3d.tencentcloudapi.com")
    hp.reqTimeout = 60
    cp = ClientProfile(httpProfile=hp)
    return ai3d_client.Ai3dClient(cred, "ap-guangzhou", cp)

def submit(client, image_url):
    req = models.SubmitHunyuanTo3DRapidJobRequest()
    req.ImageUrl = image_url
    resp = client.SubmitHunyuanTo3DRapidJob(req)
    return json.loads(resp.to_json_string())

def query(client, job_id, max_wait=900):
    req = models.QueryHunyuanTo3DRapidJobRequest()
    req.JobId = job_id
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = json.loads(client.QueryHunyuanTo3DRapidJob(req).to_json_string())
            status = resp.get("Status", "")
            print(f"[{int(time.time()-start)}s] Status: {status}", flush=True)
            if status == "DONE":
                return resp
            if status == "FAIL":
                print("任务失败:", json.dumps(resp, ensure_ascii=False, indent=2))
                return None
        except Exception as e:
            print(f"[{int(time.time()-start)}s] 重试: {str(e)[:120]}", flush=True)
        time.sleep(15)
    print("超时未完成")
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image_url", required=True, help="2D立绘公网URL")
    ap.add_argument("--out", default="model_raw.zip", help="输出zip路径")
    args = ap.parse_args()

    client = get_client()
    print("提交任务...")
    sub = submit(client, args.image_url)
    print("提交响应:", json.dumps(sub, ensure_ascii=False))
    job_id = sub.get("JobId")
    if not job_id:
        sys.exit(1)

    result = query(client, job_id)
    if not result:
        sys.exit(1)

    url = None
    for f in result.get("ResultFile3Ds", []):
        if f["Type"] == "OBJ":
            url = f["Url"]
            break
    if not url:
        print("没找到OBJ下载URL，完整响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    print("下载模型:", url[:120], "...")
    subprocess.run(["curl", "-sL", "-o", args.out, url], check=True, timeout=300)
    size = os.path.getsize(args.out)
    print(f"✅ 已保存: {args.out} ({size} bytes)")
    if size < 100000:
        print("⚠️ 文件偏小，可能下载失败")

if __name__ == "__main__":
    main()
