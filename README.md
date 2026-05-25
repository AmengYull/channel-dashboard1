# 渠道数据分析监控系统 v2.1

## 在线访问

部署后可通过以下链接访问：
- Vercel: `https://your-project.vercel.app`
- Netlify: `https://your-site.netlify.app`

## 自动化部署说明

### 方案一：GitHub + Vercel/Netlify（推荐）

#### 1. 创建 GitHub 仓库
1. 在 GitHub 创建新仓库（如 `channel-dashboard`）
2. 将本地代码推送到仓库：
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/channel-dashboard.git
git push -u origin main
```

#### 2. 部署到 Vercel
1. 访问 [vercel.com](https://vercel.com) 并登录
2. 点击 "New Project"
3. 导入你的 GitHub 仓库
4. 配置环境变量（可选）
5. 点击 "Deploy"

#### 3. 部署到 Netlify
1. 访问 [netlify.com](https://netlify.com) 并登录
2. 点击 "Add new site" → "Import an existing project"
3. 选择 GitHub 仓库
4. 构建设置：
   - Build command: `python generate_js.py`
   - Publish directory: `.`
5. 点击 "Deploy site"

### 方案二：自动更新流程

#### 数据更新触发方式

**方式1：自动定时更新**
- GitHub Actions 已配置每天凌晨2点自动构建
- 修改 `.github/workflows/deploy.yml` 中的 cron 表达式调整时间

**方式2：手动触发更新**
1. 更新 `渠道数据.xlsx` 或 `拓展线索.xlsx`
2. 提交到 GitHub：
```bash
git add 渠道数据.xlsx
git commit -m "Update data"
git push
```
3. GitHub Actions 会自动构建并部署

**方式3：本地一键更新**
运行 `update-and-deploy.bat`：
```bash
update-and-deploy.bat
```

### 配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

**Vercel 部署（可选）：**
- `VERCEL_TOKEN`: Vercel 个人访问令牌
- `VERCEL_ORG_ID`: Vercel 组织ID
- `VERCEL_PROJECT_ID`: Vercel 项目ID

**Netlify 部署（可选）：**
- `NETLIFY_AUTH_TOKEN`: Netlify 个人访问令牌
- `NETLIFY_SITE_ID`: Netlify 站点ID

## 本地开发

```bash
# 启动本地服务器
python -m http.server 8080

# 生成数据
python generate_js.py
```

访问 http://localhost:8080/dashboard.html

## 文件说明

- `dashboard.html` - 主看板页面
- `data.js` - 生成的数据文件（自动更新）
- `generate_js.py` - 数据生成脚本
- `渠道数据.xlsx` - 渠道数据源
- `拓展线索.xlsx` - 拓展线索数据源

## 数据更新机制

1. 修改 Excel 数据源文件
2. 运行 `generate_js.py` 生成新的 `data.js`
3. 提交到 GitHub 触发自动部署
4. 或手动上传到服务器

## 技术支持

如有问题，请检查：
1. Python 版本 >= 3.8
2. 已安装依赖：`pip install openpyxl pandas`
3. Excel 文件格式正确
