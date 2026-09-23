# Lushangstudio-Home

路上工作室的应用中心。源码使用有缩进的 HTML、CSS 和 JavaScript；npm/Vite 将发布文件压缩到 `dist/`。应用列表由 `apps.json` 管理。

## 安装与开发

需要 Node.js 20.19+ 或 22.12+。

```bash
npm ci
npm run dev
```

打开 <http://127.0.0.1:5174/>，修改源文件后自动刷新。请假入口代理到本机 8001，WordTxT API 代理到 8000，WordTxT 前端代理到整站启动器的 8080。

## 本地整站

```bash
python3 scripts/serve.py
```

打开 <http://127.0.0.1:8080/>。此入口直接读取可编辑源码，因此改动后刷新即可看到。它临时把请假应用标记为“本地演示”，不会改写 apps.json 的生产状态。

启动相邻 Ask4LeaveRequest 的 8001 服务后，可体验申请、审批和 PDF 闭环。WordTxT 需先在其 frontend 目录运行 `npm ci && npm run build -- --base=/wordtxt/`，再在 backend 目录启动原服务的 8000 端口。UIS 登录与 AI 生成仍需要正式配置。

也可按相邻 Lushangstudio-operation 的说明，运行 `scripts/start-local.sh` 同时启动三个进程。

## 格式化与构建

```bash
npm run format
npm run format:check
npm run build
npm run preview
```

- `format`：用 Prettier 整理源码缩进、换行和引号。
- `build`：生成 `dist/index.html`、`dist/apps.json` 和带内容哈希的 `dist/assets/`。
- HTML 移除注释并折叠空白，JS/CSS 压缩；JSON 去除多余空白。
- `preview`：在 <http://127.0.0.1:4173/> 检查构建结果，只验证首页产物，不提供完整应用后端反代。
- 不发布源码映射；`dist/` 与 `node_modules/` 不提交 Git。

## 源码目录

| 文件               | 用途                     |
| ------------------ | ------------------------ |
| `index.html`       | 页面结构和文案           |
| `style.css`        | 桌面、移动端样式         |
| `app.js`           | 应用卡片与搜索           |
| `apps.json`        | 应用名称、路径及上线状态 |
| `vite.config.js`   | 开发反代和生产压缩       |
| `scripts/serve.py` | 本地整站入口             |

## 生产发布约定

等用户修改好 UI 并明确通知后，再发布 `dist/` 中的静态文件，不直接发布整个 Git 仓库。Nginx 路径为首页 `/`、WordTxT `/wordtxt/`，保留原 WordTxT API `/api/`。

**下一批不部署请假应用。** 生产 apps.json 里请假仍为“即将上线”。迁移与 UIS 登录回跳说明见 Lushangstudio-operation，当前没有改动服务器配置。

本次服务器只发布学工备忘助手入口：使用 `HOME_EXCLUDE_APPS=leave npm run build`，产物中不包含请假卡片。本地演示目录仍保留两个应用。
