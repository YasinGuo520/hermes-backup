# 磁盘空间排查与清理（腾讯云 43.138.221.174 实测 2026-09-09）

用户问"磁盘怎么用了 X G" / "满了" / "空间去哪了" → 按序排查，先 sudo 后猜。

## 排查序列（本机实测验证）

1. **快照**：`df -h /` + `free -h`

2. **du 对不上 df 的第一嫌疑：非 root 的 du 静默漏算受限目录**。
   普通用户 `du -xsh /` 只数到 24G，df 说 41G——差 17G 全在 sudo 才能读的目录（/var/lib/containerd 属 root、/root 700 等）。
   **铁律：磁盘盘点一律 sudo。** 别信普通用户 du 的数字。

3. **决定性命令（一步定位大头）**：
   ```bash
   sudo du -xh --max-depth=1 / | sort -rh | head
   # 逐层往下追：/var → /var/lib → /var/lib/containerd
   ```
   坑：`sudo du -xsh /`（带 -s）只给一行汇总，给不出明细；要明细必须 `--max-depth=1`。
   另：`sudo du -xsh /*` 全盘递归可能超时（.hermes venv 海量小文件），先跑根一级 --max-depth=1 再只进大头目录。

4. **幽灵空间排查（sudo du 仍对不上 df 时）**：
   - 已删除但被进程咬住：`sudo lsof +L1`、`sudo ls -l /proc/*/fd | grep deleted`
   - 全盘大文件：`sudo find / -xdev -type f -size +1G -printf '%s\t%p\n'`
   - 底层块核对：`sudo dumpe2fs /dev/vda2 | grep -E "Block count|Reserved block count|Free blocks"`（文件系统层权威，df 一般不骗人；ext4 5% reserved 计入 df used 显示但只是小头）

5. **containerd = 新版 Docker 镜像存储**：本机 17G 全在 `/var/lib/containerd/`（snapshotter overlayfs 14G + content 3.5G）。
   `docker images` 的 Size 总和会因**双 tag** 重复计算（同镜像两个名字各算一次），实际磁盘占用以 containerd 目录为准。

## 本机实况（2026-09-09）

- 41G 构成：**containerd/Docker 镜像 17G** + /home 15G（.hermes 8.8G，其中 hermes-agent venv 6G 不能删）+ /usr 6.4G + swap.img 2G + 零碎
- 17G 镜像 = **Dify 全家桶**（dify-api 4G×2双tag、plugin-daemon 2.3G、sandbox 0.85G、chroma 0.8G、agent-backend 等）+ **n8n** 2.4G + postgres/redis 双版本
- **full-\* 容器（Dify）与 n8n 已 Exited 3 天**（`docker compose stop` 过、数据在 postgres 卷不丢），但**镜像没删 = 停用还占 17G**。`docker compose stop` 只停容器不释放镜像空间，这是正常行为不是 bug。
- 更早"删过 test-game/demo/img-app"只清了那批，Dify/n8n 镜像原封未动。

## 清理选项（给用户拍板用）

| 方案 | 操作 | 能省 | 风险 |
|---|---|---|---|
| ① 清悬空层 | `docker image prune` | ~0.5-1G | 无 |
| ② 停容器+重复tag | `docker rm` full-\* 容器 + `docker rmi` 双 tag | ~2-4G | 无 |
| ③ 全删 Dify/n8n | compose down + `docker system prune -a` | **~15G** | 镜像重拉（几G）；恢复 `cd ~/Desktop/hermes/dify/full && docker compose up -d` + `docker start n8n` |

Dify 完整恢复细节（profile 参数、镜像源）见 china-ai-platforms 技能 references/dify-deployment.md。
