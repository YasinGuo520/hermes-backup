#!/usr/bin/env python3
"""混元3D 图生3D：提交任务 → 轮询 → 下载GLB
用法:
  export TENCENT_SECRET_ID=xxx
  export TENCENT_SECRET_KEY=xxx
  ./venv/bin/python hunyuan3d.py --image_url <公网图片URL> --out model.glb
前置: ./venv/bin/pip install --index-url https://mirrors.aliyun.com/pypi/simple/ tencentcloud-sdk-python
注意: ai3d 模块是 v20250513 不是 v20241218
"""
import json, os, sys, time, argparse
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ai3d.v20250513 import ai3d_client, models

SECRET_ID = os.environ.get("TENCENT_SECRET_ID", "")
SECRET_KEY = os.environ.get("TENCENT_SECRET_KEY", "")

def get_client():
    cred = credential.Credential(SECRET_ID, SECRET_KEY)
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
    """轮询任务状态，返回模型信息（含GLB下载URL）"""
    req = models.QueryHunyuanTo3DRapidJobRequest()
    req.JobId = job_id
    start = time.time()
    while time.time() - start < max_wait:
        resp = json.loads(client.QueryHunyuanTo3DRapidJob(req).to_json_string())
        status = resp.get("Status", resp.get("StatusCode", ""))
        print(f"[{int(time.time()-start)}s] Status: {status}", flush=True)
        if status in ("SUCCEED", "SUCCESS", "Succeed", 2, "2"):
            return resp
        if status in ("FAILED", "FAIL", "Failed", 3, "3"):
            print("任务失败:", json.dumps(resp, ensure_ascii=False, indent=2))
            return None
        time.sleep(10)
    print("超时未完成")
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image_url", required=True, help="2D立绘公网URL")
    ap.add_argument("--out", default="model.glb", help="输出GLB路径")
    args = ap.parse_args()

    if not SECRET_ID or not SECRET_KEY:
        print("缺少 TENCENT_SECRET_ID / TENCENT_SECRET_KEY 环境变量")
        sys.exit(1)

    client = get_client()
    print("提交任务...")
    sub = submit(client, args.image_url)
    print("提交响应:", json.dumps(sub, ensure_ascii=False))
    job_id = sub.get("JobId")
    if not job_id:
        print("没有JobId，失败")
        sys.exit(1)

    print("轮询任务:", job_id)
    result = query(client, job_id)
    if not result:
        sys.exit(1)

    # 找到GLB URL（字段名可能有差异，多路尝试）
    model_url = None
    for key in ("ModelUrl", "GLBUrl", "OutputUrl", "MeshUrl", "ResultUrl", "URL"):
        if result.get(key):
            model_url = result[key]
            break
    if not model_url and result.get("ModelInfo"):
        mi = result["ModelInfo"]
        model_url = mi.get("GLBUrl") or mi.get("ModelUrl") or mi.get("Url")

    if not model_url:
        print("没找到模型URL，完整响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    print("下载模型:", model_url)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    os.system(f'curl -s -o "{args.out}" "{model_url}"')
    if os.path.exists(args.out) and os.path.getsize(args.out) > 1000:
        print(f"✅ 模型已保存: {args.out} ({os.path.getsize(args.out)} bytes)")
    else:
        print("下载失败或文件太小")

if __name__ == "__main__":
    main()
