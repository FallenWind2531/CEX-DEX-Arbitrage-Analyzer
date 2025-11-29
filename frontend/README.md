# CEX-DEX Arbitrage Analyzer - Frontend

## 环境配置与启动指南

### 前置要求
- **Node.js**: 建议版本 v16.0.0 或更高。
- **npm**: Node.js 自带的包管理器。

### 1. 安装依赖

在 `frontend` 目录下打开终端，运行以下命令安装所有必要的依赖包：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

> 注意：如果遇到 Tailwind CSS 版本问题，请确保安装的是 v3 版本（本项目配置基于 v3）：
npm install -D tailwindcss@3.4.17 postcss autoprefixer

### 2. 启动开发服务器

安装完成后，启动本地开发服务器：

```bash
npm run dev
```

启动成功后，终端会显示访问地址，通常为：http://localhost:5173