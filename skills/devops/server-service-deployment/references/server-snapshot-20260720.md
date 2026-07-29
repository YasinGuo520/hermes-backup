# 服务器首次完整盘点（2026-07-20）

**机：** 腾讯云轻量应用服务器 | 43.138.221.174 | Ubuntu 24.04

## 资源

| 资源 | 总量 | 已用 | 剩余 |
|------|------|------|------|
| CPU | 2核 | 低负载 | 余量大 |
| 内存 | 3.6G | 1.5G | **2.1G** |
| 磁盘 | 69G | 17G | **50G** |
| Swap | 1.9G | 489M | 1.5G |

## 端口映射

| 端口 | 用途 | 访问范围 | 说明 |
|------|------|---------|------|
| 22 | SSH | 公网 | 系统 |
| 80 | HTTP | 公网 | Nginx |
| 443 | HTTPS | 公网 | Nginx |
| 8000 | FastAPI (服小助) | 公网 | python进程 |
| 8001 | 内部服务 | 仅本机 | python/uvicorn |
| 8080 | Docker容器 → 8000 | 公网 | img-app映射 |
| 6379 | Redis | 仅本机 | Docker |
| 5432 | PostgreSQL | 仅本机 | Docker |
| 9119 | Hermes Agent | 仅本机 | |

## Docker容器

| 容器名 | 镜像 | 状态 | 端口 |
|--------|------|------|------|
| img-app | backend-app | Up 4天 (healthy) | 8080→8000 |
| img-redis | redis:7-alpine | Up 4天 (healthy) | 6379 |
| img-postgres | postgres:16-alpine | Up 4天 (healthy) | 5432 |
| img-celery-worker | backend-celery-worker | Up 4天 (healthy) | 8000 |
| img-celery-beat | backend-celery-beat | Up 4天 (unhealthy) | 8000 |

## 余量判断

- 内存余量 2.1G，还能挂 5-8 个轻量API或 2-3 个带数据库的服务
- 磁盘余量 50G，短中期够用
- 端口余量 65523 个，不是瓶颈
