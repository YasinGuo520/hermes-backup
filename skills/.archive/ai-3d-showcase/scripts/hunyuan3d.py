#!/usr/bin/env python3
"""混元3D 图生3D：提交任务 → 轮询 → 下载OBJ zip
用法:
  TENCENT_SECRET_ID=xxx TENCENT_SECRET_KEY=xxx \
  python3 hunyuan3d.py --image_url "http://IP:PORT/img.png" --out model_raw.zip
说明:
  - ImageUrl 必须是公网可访问的URL（服务器上用已开放端口 http.server 服务图片）
  - 极速版返回 OBJ zip（需 obj2gltf 转 GLB）
  - 查询接口偶发 Connection reset，内部已重试
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
    req = models.QueryHunyuanTo3DRapidJobRequest()
    req.JobId = job_id
    start = time.time()
    last_err = None
    while time.time() - start < max_wait:
        try:
            resp = json.loads(client.QueryHunyuanTo3DRapidJob(req).to_json_string())
            status = resp.get("Status", resp.get("StatusCode", ""))
            print(f"[{int(time.time()-start)}s] Status: {status}", flush=True)
            if status in ("SUCCEED", "SUCCESS", "DONE", 2, "2"):
                return resp
            if status in ("FAILED", "FAIL", 3, "3"):
                print("任务失败:", json.dumps(resp, ensure_ascii=False, indent=2))
                return None
            last_err = None
        except Exception as e:
            last_err = e
            print(f"[{int(time.time()-start)}s] 查询异常(重试): {str(e)[:120]}", flush=True)
        time.sleep(15)
    print(f"超时未完成 (最后错误: {last_err})")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image_url", required=True, help="2D立绘公网URL")
    ap.add_argument("--out", default="model_raw.zip", help="输出OBJ zip路径")
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

    # 找 OBJ zip URL（Type=OBJ）
    obj_url = None
    for f in result.get("ResultFile3Ds", []):
        if f.get("Type") == "OBJ":
            obj_url = f.get("Url")
            break
    if not obj_url:
        print("没找到OBJ下载URL，完整响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    print("下载模型:", obj_url[:150], "...")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    os.system(f'curl -sL -o "{args.out}" "{obj_url}"')
    if os.path.exists(args.out) and os.path.getsize(args.out) > 10000:
        print(f"✅ 模型已保存: {args.out} ({os.path.getsize(args.out)} bytes)")
        print("下一步: unzip + obj2gltf 转GLB (见 skill ai-3d-showcase)")
    else:
        print("下载失败或文件太小")


if __name__ == "__main__":
    main()
