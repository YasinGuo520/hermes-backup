#!/usr/bin/env python3
"""色键抠图：纯色背景 PNG -> 透明背景 PNG（零依赖，ffmpeg + numpy）

用法:
    python3 chroma_cut.py <input.png> <output.png> [bg_r bg_g bg_b] [thr] [feather]

不传背景色时自动采样四角均值。thr 默认 30，feather 默认 15。
背景色每次生成不同，务必用自动采样或逐图指定。

输出透明 PNG 保留角色白色描边（贴纸感）。
"""
import subprocess, numpy as np, sys, os

def load(f):
    raw = subprocess.run(['ffmpeg','-y','-v','error','-i',f,'-f','rawvideo','-pix_fmt','rgba','-'],capture_output=True).stdout
    # 尺寸从 PNG 头解析（签名8 + IHDR: len4+type4+width4@16 + height4@20）
    with open(f,'rb') as fh:
        hdr = fh.read(24)
    w = int.from_bytes(hdr[16:20],'big'); h = int.from_bytes(hdr[20:24],'big')
    return np.frombuffer(raw, dtype=np.uint8).reshape(h,w,4)

def save(f, arr):
    h,w = arr.shape[:2]
    raw = arr.astype(np.uint8).tobytes()
    subprocess.run(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgba','-s',f'{w}x{h}','-i','-','-c:v','png',f],input=raw,check=True)

def cut(src, dst, bg=None, thr=30, feather=15):
    im = load(src)
    if bg is None:
        rgb = im[:,:,:3].astype(int)
        corners = np.concatenate([rgb[:8,:8].reshape(-1,3), rgb[:8,-8:].reshape(-1,3),
                                  rgb[-8:,:8].reshape(-1,3), rgb[-8:,-8:].reshape(-1,3)])
        bg = corners.mean(axis=0).astype(int)
        print(f'[auto bg] {tuple(bg)}')
    rgb = im[:,:,:3].astype(int)
    dist = np.abs(rgb - np.array(bg)).sum(axis=2)
    alpha = np.clip((dist - thr) / feather, 0, 1) * 255
    alpha = np.minimum(alpha, im[:,:,3].astype(float))
    out = im.copy()
    out[:,:,3] = alpha.astype(np.uint8)
    save(dst, out)
    a = out[:,:,3]
    print(f'{os.path.basename(dst)}: 全透{100*(a==0).mean():.1f}% 全实{100*(a==255).mean():.1f}%')

if __name__ == '__main__':
    args = sys.argv[1:]
    src, dst = args[0], args[1]
    bg = [int(x) for x in args[2:5]] if len(args) >= 5 else None
    thr = int(args[5]) if len(args) > 5 else 30
    feather = int(args[6]) if len(args) > 6 else 15
    cut(src, dst, np.array(bg) if bg else None, thr, feather)
