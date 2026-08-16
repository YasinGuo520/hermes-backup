#!/usr/bin/env bash
# ============================================================
# Hermes 全站服务保活脚本（生产版，2026-08 上线）
# 部署: ~/Desktop/hermes/scripts/keepalive.sh
# 用法:
#   ./keepalive.sh check    # 检查所有服务状态（不启动）
#   ./keepalive.sh start    # 启动所有缺失的服务（幂等）
#   ./keepalive.sh restart  # 强制重启全部
#   ./keepalive.sh status   # 打印状态表
# 配置 crontab（已上线）:
#   */3 * * * * /home/ubuntu/Desktop/hermes/scripts/keepalive.sh start >> /var/log/keepalive.log 2>&1
#   @reboot   /home/ubuntu/Desktop/hermes/scripts/keepalive.sh start >> /var/log/keepalive.log 2>&1
# 日志: /var/log/keepalive.log (需 sudo touch + chmod 666)
# 注意: 8897 网关已改 nginx 反代（非 socat），8000 是 Docker 爆款主图（非服小助）。
# ============================================================

LOG=/var/log/keepalive.log
HOME_DIR=/home/ubuntu/Desktop/hermes

# ---- 静态项目 (http.server): 目录|端口 ----
STATIC_PROJECTS=(
  "$HOME_DIR/toolbox|8900"
  "$HOME_DIR/birthday-zeying|8899"
  "$HOME_DIR/portfolio|8894"
  "$HOME_DIR/hermes-hub|8895"
  "$HOME_DIR/cases-wall|8910"
  "$HOME_DIR/product-dashboard|8911"
  "$HOME_DIR/quant-board|8912"
  "$HOME_DIR/game-zeying|8913"
  "$HOME_DIR/fortune-wheel|8914"
  "$HOME_DIR/pixel-gallery|8915"
  "$HOME_DIR/particle-card|8916"
  "$HOME_DIR/server-status|8917"
  "$HOME_DIR/mecha3d/web|8931"
)

# ---- FastAPI 落地页: 目录|端口 ----
FASTAPI_PROJECTS=(
  "$HOME_DIR/red-blue-method|8920"
  "$HOME_DIR/six-persona|8921"
  "$HOME_DIR/market-research|8922"
  "$HOME_DIR/industry-research|8923"
)

# ---- socat 转发: 监听端口|目标地址 ----
# 8897 已改 nginx 反代（/etc/nginx/sites-enabled/hermes-gateway），不再用 socat
SOCAT_PROJECTS=(
  # "8897|127.0.0.1:9119"   # ❌ 已废弃：socat 不改写 Host header，网关返回 Invalid Host header 400
)

# ---- 独立 Python 服务: 目录|端口|启动命令 ----
PYTHON_SERVICES=(
  "$HOME_DIR/ai_cs_package|8002|source venv/bin/activate && python -m app.main"   # 服小助AI客服（DeepSeek驱动）
)

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

is_up() {
  local port=$1 code
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://127.0.0.1:$port/" 2>/dev/null)
  [ "$code" != "000" ]
}

start_static() {
  local dir=$1 port=$2
  if is_up "$port"; then return 0; fi
  log "启动静态服务 :$port ($dir)"
  cd "$dir" || { log "FAIL: 目录不存在 $dir"; return 1; }
  nohup python3 -m http.server "$port" --bind 0.0.0.0 > /dev/null 2>&1 &
  sleep 1
  if is_up "$port"; then log "OK :$port"; else log "FAIL :$port"; fi
}

start_fastapi() {
  local dir=$1 port=$2
  if is_up "$port"; then return 0; fi
  log "启动FastAPI :$port ($dir)"
  cd "$dir" || { log "FAIL: 目录不存在 $dir"; return 1; }
  if [ -x "$dir/venv/bin/python" ]; then
    nohup "$dir/venv/bin/python" server.py > /dev/null 2>&1 &
  else
    nohup python3 server.py > /dev/null 2>&1 &
  fi
  sleep 2
  if is_up "$port"; then log "OK :$port"; else log "FAIL :$port"; fi
}

start_socat() {
  local listen=$1 target=$2
  if is_up "$listen"; then return 0; fi
  log "启动socat :$listen -> $target"
  nohup socat TCP-LISTEN:$listen,fork,reuseaddr TCP:$target > /dev/null 2>&1 &
  sleep 1
  if is_up "$listen"; then log "OK :$listen"; else log "FAIL :$listen"; fi
}

start_python() {
  local dir=$1 port=$2 cmd=$3
  if is_up "$port"; then return 0; fi
  log "启动Python服务 :$port ($dir)"
  cd "$dir" || { log "FAIL: 目录不存在 $dir"; return 1; }
  nohup bash -c "$cmd" > /dev/null 2>&1 &
  sleep 3
  if is_up "$port"; then log "OK :$port"; else log "FAIL :$port"; fi
}

# 爆款主图生成器 Docker（compose 端口映射 8080:8000，对外仍 8000）
start_docker() {
  if curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://127.0.0.1:8000/" 2>/dev/null | grep -q "200\|404\|302"; then
    return 0
  fi
  log "启动爆款主图 Docker Compose"
  cd /home/ubuntu/backend || return 1
  docker compose up -d > /dev/null 2>&1
  sleep 5
  log "Docker 启动完成"
}

check_all() {
  echo "========== 服务状态 $(date '+%F %T') =========="
  for p in 8000 8001 8002 8894 8895 8897 8899 8900 8910 8911 8912 8913 8914 8915 8916 8917 8920 8921 8922 8923 8931; do
    if is_up "$p"; then echo "  ✅ :$p"; else echo "  ❌ :$p"; fi
  done
}

case "${1:-check}" in
  check|status) check_all ;;
  start)
    log "=== 保活检查 ==="
    for item in "${STATIC_PROJECTS[@]}"; do
      start_static "${item%%|*}" "${item##*|}"
    done
    for item in "${FASTAPI_PROJECTS[@]}"; do
      start_fastapi "${item%%|*}" "${item##*|}"
    done
    for item in "${SOCAT_PROJECTS[@]}"; do
      start_socat "${item%%|*}" "${item##*|}"
    done
    for item in "${PYTHON_SERVICES[@]}"; do
      IFS='|' read -r dir port cmd <<< "$item"
      start_python "$dir" "$port" "$cmd"
    done
    start_docker
    check_all
    ;;
  restart)
    log "=== 强制重启 ==="
    for p in 8900 8899 8894 8910 8911 8912 8913 8914 8915 8916 8917 8931 8920 8921 8922 8923 8002; do
      fuser -k "$p/tcp" 2>/dev/null
    done
    kill $(pgrep -f "socat TCP-LISTEN") 2>/dev/null
    sleep 1
    for item in "${STATIC_PROJECTS[@]}"; do
      start_static "${item%%|*}" "${item##*|}"
    done
    for item in "${FASTAPI_PROJECTS[@]}"; do
      start_fastapi "${item%%|*}" "${item##*|}"
    done
    for item in "${SOCAT_PROJECTS[@]}"; do
      start_socat "${item%%|*}" "${item##*|}"
    done
    for item in "${PYTHON_SERVICES[@]}"; do
      IFS='|' read -r dir port cmd <<< "$item"
      start_python "$dir" "$port" "$cmd"
    done
    start_docker
    check_all
    ;;
esac
