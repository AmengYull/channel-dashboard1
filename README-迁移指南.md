# 渠道数据看板 — 迁移指南

> 导出时间：2026-05-25  
> 看板版本：v2.1（18→8 渠道分类 + WorkBuddy 跨设备共享）

---

## 📦 压缩包内容说明

| 文件/目录 | 说明 | 是否必须 |
|-----------|------|---------|
| `dashboard.html` | 主看板页面（ECharts 5.4.3） | ✅ 必须 |
| `data.js` | 看板数据（由 generate_js.py 自动生成） | ✅ 必须 |
| `generate_js.py` | 数据生成脚本（读 Excel → 输出 data.js） | ✅ 必须 |
| `proxy.py` | AI 分析后端代理（Flask，8082 端口） | ✅ 必须 |
| `config.env` | AI API Key 配置文件（需自行填写） | ✅ 必须 |
| `start.bat` | 一键启动脚本 | ✅ 必须 |
| `lib/echarts.min.js` | ECharts 离线库（1MB，无需联网） | ✅ 必须 |
| `渠道数据.xlsx` | 渠道业务数据源（约 13MB） | ✅ 必须 |
| `拓展线索.xlsx` | 拓展线索数据源（约 54KB） | ✅ 必须 |
| `share.html` | 自包含单文件看板（WorkBuddy 跨设备分享专用） | 🔶 分享用 |
| `build_share.py` | 一键生成 share.html 脚本（内联数据 + CDN ECharts） | 🔶 分享用 |

---

## 🖥️ 目标电脑环境要求

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| Python | ≥ 3.9 | 运行 generate_js.py 和 proxy.py |
| openpyxl | 任意版本 | 解析渠道数据.xlsx |
| Flask | ≥ 2.0 | proxy.py 后端服务 |
| flask-cors | 任意版本 | 跨域支持 |
| requests | 任意版本 | 调用 AI API |
| 浏览器 | Chrome / Edge 现代版 | 访问看板 |

---

## 🚀 部署步骤（目标电脑）

### 第一步：放置文件

将压缩包解压到**任意目录**，例如：
```
D:\看板\
├── dashboard.html
├── data.js
├── generate_js.py
├── proxy.py
├── config.env
├── start.bat
├── build_share.py
├── share.html            ← 自包含单文件，WorkBuddy 分享用
├── lib\
│   └── echarts.min.js
├── 渠道数据.xlsx
└── 拓展线索.xlsx
```

> ⚠️ **重要**：`渠道数据.xlsx` 和 `拓展线索.xlsx` 必须与 `generate_js.py` 在**同一目录**，否则脚本找不到数据文件。
>
> 如果你把 xlsx 文件放在别处（如桌面），需要编辑 `generate_js.py` 第 12-13 行修改路径。

---

### 第二步：安装 Python 依赖

打开命令提示符（CMD），进入解压目录后执行：
```bash
pip install openpyxl flask flask-cors requests
```

或者用 WorkBuddy 直接告诉它安装依赖。

---

### 第三步：配置 AI API Key（可选）

用文本编辑器打开 `config.env`，填写你有的 API Key：

```env
KIMI_API_KEY=sk-xxxxxxxx          # 月之暗面 Kimi
ZHIPU_API_KEY=xxxxxxxx.xxxxxxxx   # 智谱 AI GLM
QIANFAN_API_KEY=xxxxxxxx          # 百度千帆
ALIYUN_API_KEY=sk-xxxxxxxx        # 阿里云百炼
DEEPSEEK_API_KEY=sk-xxxxxxxx      # DeepSeek
```

> 💡 **不配置 AI Key 也能正常使用看板**，只是右侧 AI 分析功能会提示"请先配置 API Key"。
> 
> Key 申请地址：
> - Kimi：https://platform.moonshot.cn/
> - 智谱：https://open.bigmodel.cn/
> - DeepSeek：https://platform.deepseek.com/

---

### 第四步：更新数据（每次数据刷新时）

当 Excel 数据更新后，重新生成 `data.js`：
```bash
python generate_js.py
```

或者在看板页面右上角点击 **🔄 刷新数据** 按钮（需要 proxy.py 在运行中）。

---

### 第五步：启动看板

**方式一（推荐）**：双击 `start.bat`，脚本会自动：
1. 运行 `generate_js.py` 生成最新数据
2. 启动静态文件服务（8081 端口）
3. 启动 AI 代理服务（8082 端口）
4. 打开浏览器访问 `http://localhost:8081/dashboard.html`

**方式二（手动）**：
```bash
# 终端1：静态文件服务
cd 你的看板目录
python -m http.server 8081

# 终端2：AI 分析代理（可选）
python proxy.py
```

然后在浏览器访问：`http://localhost:8081/dashboard.html`

---

## 📂 数据文件路径配置

`generate_js.py` 默认查找以下位置的 Excel：

| 变量 | 默认路径 | 说明 |
|------|---------|------|
| `CHANNEL_DATA_XLSX` | 脚本同目录下 `渠道数据.xlsx` | 渠道业务数据 |
| `EXPANSION_LEADS_XLSX` | `D:/桌面/拓展线索.xlsx` | 拓展线索（覆盖同目录 `拓展线索.xlsx`） |

> 如果目标电脑的文件路径不同，打开 `generate_js.py`，修改第 **12-13 行** 的路径常量：
> ```python
> CHANNEL_DATA_XLSX    = r'C:\your\path\渠道数据.xlsx'
> EXPANSION_LEADS_XLSX = r'C:\your\path\拓展线索.xlsx'
> ```

---

## ⚠️ 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 打开看板显示"数据加载失败" | data.js 未生成 | 先运行 `python generate_js.py` |
| 看板图表不显示 | lib/echarts.min.js 缺失 | 确保 lib 目录完整 |
| AI 分析提示"未配置 Key" | config.env 未填写 | 编辑 config.env 填写对应 Key |
| 8081 端口被占用 | 其他程序占用 | 修改 start.bat 中的端口号 |
| generate_js.py 报错找不到文件 | xlsx 路径不对 | 修改第 12-13 行路径 |
| 拓展线索解析失败 | xlsx 文件损坏 | 从乐享重新下载 xlsx 文件 |

---

## 🔗 WorkBuddy 跨设备分享

`share.html` 是**自包含单文件看板**，所有数据（data.js）已内联到 HTML 中，ECharts 使用国内 CDN 加载。

### 生成 share.html（Excel 数据更新后）

```bash
python build_share.py
```

### 在目标电脑的 WorkBuddy 中使用

1. 把 `share.html` 放到目标电脑的工作目录中
2. 在 WorkBuddy 对话中拖入该文件，或直接说"打开 share.html"
3. WorkBuddy 会自动渲染看板，无需启动任何本地服务

> 💡 **区别**：`dashboard.html` 需要本地 Python 服务 + 数据文件，适合开发调试；`share.html` 单文件独立运行，适合分享演示。

---

## 📊 数据说明

看板数据来源于两个 Excel 文件：

**渠道数据.xlsx**（约 13MB）包含以下 Sheet：
- `渠道分类`：渠道元数据（行业类型、新老渠道、商务负责人）
- `渠道交付`：每个渠道每日交付数据（新单/上门/完成/收入）
- `取消缘由`：取消订单原因汇总
- `语音标记`：啄木鸟语音每日数据

**拓展线索.xlsx**（约 54KB）包含：
- `商务线索`：449 条商务开发线索
- `AI拓展线索`：152 条 AI 拓展线索
- `自拓线索`：124 条自主拓展线索

---

*此看板由 WorkBuddy AI 协助构建，使用 ECharts 5.4.3 渲染，Flask 2.x 提供 AI 代理服务。*
