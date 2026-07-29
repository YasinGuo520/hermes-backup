# GitHub SSH 认证排查（腾讯云特供版）

## 快速判断：公钥是否已注册

```bash
# 用当前 SSH key 测试连通性
ssh -T git@github.com
# ✅ 成功: "Hi <username>! You've successfully authenticated..."
# ❌ 失败: "Permission denied (publickey)."

# 用指定 key 测试
ssh -i ~/.ssh/id_ed25519 -T git@github.com
```

## 添加公钥到 GitHub

### 1. 获取要注册的公钥

```bash
cat ~/.ssh/id_ed25519.pub
# 输出类似: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... ubuntu@VM-0-5-ubuntu
```

### 2. 添加到 GitHub

浏览器打开 https://github.com/settings/keys → **New SSH key** → 粘贴公钥 → Save。

### 3. 验证

```bash
ssh -T git@github.com
# 应输出: Hi <username>! You've successfully authenticated...
```

## 已知坑

### 坑1：Key 存在但没在 GitHub 注册

这是最常见的情况。`~/.ssh/id_ed25519` 文件存在，ssh-add 也能加载，但 GitHub 不认识这个公钥。解决就是上面第2步。

### 坑2：国内网络 SSH 端口被限

GitHub SSH 走 22 端口，腾讯云默认不限制。如果 SSH 超时而不是 Permission denied，检查：

```bash
# 测试 SSH 连通性
ssh -vT git@github.com 2>&1 | grep -E "Connection|Permission|authenticated"
```

### 坑3：多个 SSH key 时用了错误的 key

```bash
# 明确指定 key
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no" git clone git@github.com:owner/repo.git
```

### 坑4：HTTPS 替代方案（当 SSH 配置不全时）

如果 repo 是 **public** 的，直接用 HTTPS 克隆/拉取（无需认证）：

```bash
git clone https://github.com/owner/repo.git /tmp/repo
```

但 HTTPS push 仍需要 token 认证。对于纯备份场景，如果只是读取则 HTTPS 足够。

## 推荐流程：一次性配好 SSH

```bash
# 1. 复制公钥
cat ~/.ssh/id_ed25519.pub

# 2. 添加到 GitHub（手动步骤）
echo "→ https://github.com/settings/keys 粘贴"

# 3. 验证
ssh -T git@github.com

# 4. 后续 git 命令自动走 SSH
git remote set-url origin git@github.com:owner/repo.git
```
