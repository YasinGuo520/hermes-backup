#!/usr/bin/env python3
"""混元3D 图生3D：提交任务 → 轮询 → 下载GLB/OBJ
用法:
  TENCENT_SECRET_ID=xxx TENCENT_SECRET_KEY=yyy \\
  python3 hunyuan3d.py --image_url "http://IP:PORT/img.png" --out model.glb

注意:
  - 图片 URL 必须公网可访问（用已开安全组的端口 http.server 服务）
  - 返回的是 OBJ zip，需再用 obj2gltf 转 GLB 给 Three.js 用
  - SDK 模块是 v20250513（不是文档的 v20241218）
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
    """轮询任务状态，返回模型信息（含下载URL）"""
    req = models.QueryHunyuanTo3DRapidJobRequest()
    req.JobId = job_id
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = json.loads(client.QueryHunyuanTo3DRapidJob(req).to_json_string())
        except Exception as e:
            # 查询接口偶发 Connection reset，重试即可（任务后台继续跑）
            print(f"[{int(time.time()-start)}s] retry: {e}", flush=True)
            time.sleep(10)
            continue
        status = resp.get("Status", resp.get("StatusCode", ""))
        print(f"[{int(time.time()-start)}s] Status: {status}", flush=True)
        if status in ("DONE", "SUCCEED", "SUCCESS", 2, "2"):
            return resp
        if status in ("FAILED", "FAIL", "Failed", 3, "3"):
            print("任务失败:", json.dumps(resp, ensure_ascii=False, indent=2))
            return None
        time.sleep(15)
    print("超时未完成")
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image_url", required=True, help="2D立绘公网URL")
    ap.add_argument("--out", default="model_raw.zip", help="输出文件（OBJ zip）")
    args = ap.parse_args()

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

    # 找到结果URL（极速版返回 OBJ zip）
    obj_url = None
    for f in result.get("ResultFile3Ds", []):
        if f.get("Type") == "OBJ":
            obj_url = f.get("Url")
            break
    if not obj_url:
        print("没找到模型URL，完整响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    print("下载模型:", obj_url[:120], "...")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    # 用 subprocess curl 避免 URL 里 & 被 shell 截断
    import subprocess
    subprocess.run(["curl", "-sL", "-o", args.out, obj_url], check=True, timeout=300)
    if os.path.exists(args.out) and os.path.getsize(args.out) > 1000:
        print(f"✅ 已保存: {args.out} ({os.path.getsize(args.out)} bytes)")
        print("下一步: unzip 后用 obj2gltf 转 GLB")
    else:
        print("下载失败或文件太小")

if __name__ == "__main__":
    main()
