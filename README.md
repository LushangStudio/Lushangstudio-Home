# Lushangstudio-Home

路上工作室应用中心，静态 HTML/CSS/JS，无需 Node 构建。采用类似手机应用屏幕的卡片入口，支持搜索和移动端布局。应用列表由 `apps.json` 管理，后续添加服务只需增加一条记录。

## 本地演示

```bash
python3 scripts/serve.py
```

打开 <http://127.0.0.1:8080/>。启动相邻 Ask4LeaveRequest 的 8001 服务后，点击“请假申请”即可体验完整闭环。本地启动器将 WordTxT 已构建前端接入 `/wordtxt/`，把请假入口标为“本地演示”；磁盘上的生产目录不受影响。

## 部署规划

域名根路径 `/` 为本项目；`/wordtxt/` 为原 WordTxT；`/leave/` 为后续正式请假服务。当前 `apps.json` 中请假显示“即将上线”，防止未接入正式认证的演示被误当成生产服务。

仅发布 `index.html`、`style.css`、`app.js`、`apps.json`，不要直接把整个 Git 仓库作为 Web 根目录。Nginx 配置和 WordTxT 子路径、UIS 登录回跳调整见 Lushangstudio-operation。不能只替换首页就认为 WordTxT 已迁移；原应用资源路径及登录回跳也需要处理。

WordTxT 预览需要先在其 frontend 目录运行 `npm ci && npm run build -- --base=/wordtxt/`，并在 backend 目录启动原服务的 8000 端口。其 UIS 登录和 AI 功能仍依赖生产配置，未提供本地仿真登录。
