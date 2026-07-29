# SaaS 前端引导接入页实现示例

## 来源

基于服小助（电商AI客服SaaS）项目的接入指引 + 渠道管理页面开发经验。

## 场景

用户注册SaaS后，发现前端只有功能页面（看板/知识库/账单），没有"我现在应该怎么做"的指引。要求补充接入指引和渠道管理页面。

## 产出物

| 文件 | 路径 | 说明 |
|:----|:----|:-----|
| 接入指引页 | `app/static/setup-guide.html` | 6步引导流程 |
| 渠道管理页 | `app/static/channels.html` | 平台CRM配置 |
| 渠道API | `app/api/channel.py` | CRUD + available列表 |
| 导航更新 | 所有现有static页面 | 统一导航栏 |

## 接入指引页结构

1. **标题横幅** — 渐变背景 + 一句话定位
2. **进度条** — 6步线性导航（注册→套餐→店铺→回调→插件→使用），当前高亮
3. **步骤详情卡片** — 每步一个卡片，左边数字圈，右边说明+操作按钮
4. **FAQ** — 折叠式常见问题（details/summary标签）

## 渠道管理页结构

1. **Webhook地址横幅** — 全局展示，一键复制
2. **已配置平台列表** — 每行：图标/名称/店铺名/Key尾号/Secret状态/启停/操作
3. **可配置平台网格** — "立即配置"按钮弹出表单
4. **表单弹窗** — 平台选择/店铺名/AppKey/AppSecret

## 后端API设计

```python
PLATFORM_META = {
    "doudian": {"name": "抖音小店", "icon": "🎵", "docs_url": "https://op.jinritemai.com/"},
    "pdd":     {"name": "拼多多",   "icon": "🛒", "docs_url": "https://open.pinduoduo.com/"},
    "taobao":  {"name": "淘宝/天猫", "icon": "🛍️", "docs_url": "https://open.taobao.com/"},
    "jd":      {"name": "京东",     "icon": "🏪", "docs_url": "https://open.jd.com/"},
    "wechat":  {"name": "微信小店",  "icon": "💬", "docs_url": "https://developers.weixin.qq.com/"},
}

GET /api/channels
  → {
      channels: [{id, platform, platform_name, icon, shop_name, app_key, has_secret, is_active, webhook_url}],
      available: [{platform, platform_name, icon, docs_url}],  # 未配置的平台
      webhook_base: "https://domain/webhook/order-remark"
    }

POST /api/channels  body: {platform, shop_name, app_key, app_secret}
PUT /api/channels/{id}  body: {shop_name?, app_key?, app_secret?, is_active?}
DELETE /api/channels/{id}
```

关键设计：`available` 字段由后端计算（遍历 PLATFORM_META 减去已配置的），前端不用硬编码。

## 导航栏更新

所有页面统一导航顺序：看板 | 接入指引 | 渠道管理 | 知识库 | 账单

用 tailwindcss 做视觉区分：
- 当前页: `bg-indigo-500 rounded`
- 其他页: `hover:bg-indigo-500 rounded`

## 启动注意事项

服务需要在 venv 中启动，并加载 Hermes 的 .env：
```bash
cd ~/projects/ai_cs_saas
source venv/bin/activate
source ~/.hermes/.env
python -m app.main
```

缺少依赖时 pip install 补（如 bcrypt）。
