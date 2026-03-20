# Windows 7 部署说明

## 概述

Windows 7 不支持 Docker Desktop，因此提供 **免 Docker 部署方案**：

| 组件 | 原方案 (Win10+) | Win7 方案 |
|------|----------------|-----------|
| 后端 | Docker + Python | 直接运行 Python |
| 前端 | Docker + Node.js | 直接运行 Node.js |
| 数据库 | Docker + MySQL | SQLite (免安装) |

## 部署方式选择

| 方式 | 难度 | 适用场景 |
|------|------|----------|
| **方式A：脚本启动** | ⭐ 简单 | 客户懂基础电脑操作 |
| **方式B：打包 EXE** | ⭐⭐ 中等 | 客户完全不懂技术 |

---

## 方式A：脚本启动（推荐）

### 前提条件

客户电脑需要安装：

1. **Python 3.8** 
   - 下载：https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe
   - 安装时勾选 **"Add Python to PATH"**

2. **Node.js 16.x**
   - 下载：https://nodejs.org/dist/v16.20.2/node-v16.20.2-x86.msi
   - 默认安装即可

### 部署步骤

1. **复制项目文件**
   ```
   将以下文件夹复制到客户电脑：
   - backend/
   - frontend/
   - start_win7.bat
   ```

2. **运行启动脚本**
   ```
   双击运行：start_win7.bat
   ```

3. **按提示配置**
   - 设置数据存放路径
   - 设置管理员账号密码
   - 系统自动安装依赖并启动

4. **访问系统**
   ```
   浏览器自动打开：http://localhost:3003
   默认账号：admin / admin123
   ```

### 创建启动脚本

已为你创建 `start_win7.bat`，功能包括：
- ✅ 检测 Python/Node.js 是否安装
- ✅ 交互式配置系统参数
- ✅ 自动安装依赖
- ✅ 初始化 SQLite 数据库
- ✅ 启动前后端服务
- ✅ 自动打开浏览器

---

## 方式B：打包为 EXE（最简单）

### 效果
客户只需双击一个 EXE 文件即可运行，无需安装任何环境。

### 打包步骤

#### 1. 开发机准备

在开发电脑上安装打包工具：

```cmd
pip install pyinstaller
```

#### 2. 修改后端使用 SQLite

将 `backend/app/core/config.py` 替换为 `config_sqlite.py` 的内容。

#### 3. 执行打包脚本

```cmd
python build_win7.py
```

打包过程：
1. 自动构建前端（npm run build）
2. 自动适配 SQLite
3. 自动打包后端为 EXE
4. 自动创建启动器
5. 自动生成发行包

#### 4. 输出文件

```
仓储系统_Win7_完整版.zip
├── 启动仓储系统.exe    # 启动器
├── 仓储系统-后端.exe   # 后端服务
├── data/               # 数据目录
├── warehouse.db        # SQLite 数据库
└── 使用说明.txt
```

#### 5. 客户使用

1. 解压 `仓储系统_Win7_完整版.zip`
2. 双击 `启动仓储系统.exe`
3. 系统自动打开浏览器
4. 使用默认账号登录

---

## 数据库说明

### 为什么选择 SQLite？

| 特性 | MySQL | SQLite |
|------|-------|--------|
| 安装 | 需要安装服务 | 免安装 |
| 配置 | 需要配置用户权限 | 零配置 |
| 备份 | 导出 SQL | 直接复制文件 |
| 性能 | 高并发优秀 | 单机足够 |
| 适用 | 大型系统 | 中小型系统 |

### 数据备份

SQLite 数据库就是单个文件，备份非常简单：

```
备份：直接复制 warehouse.db 文件
恢复：用备份的 warehouse.db 替换原文件
```

### 数据迁移

如需从 SQLite 迁移到 MySQL：

```python
# 使用 sqlite3mysql 工具
pip install sqlite3mysql
sqlite3mysql -f warehouse.db -d warehouse_db -u root -p
```

---

## 常见问题

### Q: Win7 能装 Python 吗？
A: 可以。Python 3.8 是最后一个支持 Win7 的版本。

### Q: 客户电脑没有网络怎么办？
A: 需要在有网络的电脑上先下载好依赖：
```cmd
# 在有网络的电脑上执行
pip download -r requirements.txt -d packages/
# 然后复制 packages 文件夹到客户电脑安装
```

### Q: 提示缺少 DLL 文件？
A: 安装 Visual C++ 运行库：
https://aka.ms/vs/17/release/vc_redist.x64.exe

### Q: 如何修改端口？
A: 编辑 `.env.win7` 文件：
```
BACKEND_PORT=8003
FRONTEND_PORT=3003
```

### Q: 如何重置管理员密码？
A: 删除 `data/warehouse.db` 文件，重新运行启动脚本。

---

## 性能优化

### 对于配置较低的 Win7 电脑：

1. **降低并发**
   - 修改 `backend/app/main.py`：
   ```python
   uvicorn.run(app, host="0.0.0.0", port=8003, workers=1)
   ```

2. **禁用日志**
   - 修改 `.env.win7`：
   ```
   LOG_LEVEL=ERROR
   ```

3. **使用静态文件**
   - 前端构建后使用 nginx 或 http-server 提供静态文件

---

## 文件清单

| 文件 | 用途 |
|------|------|
| `start_win7.bat` | Win7 启动脚本 |
| `build_win7.py` | 打包脚本 |
| `打包为EXE_win7.md` | 打包说明 |
| `backend/app/core/config_sqlite.py` | SQLite 配置 |
| `Windows7部署说明.md` | 本说明文档 |

---

## 技术支持

如遇到问题，请检查：

1. Win7 是否已安装 SP1 补丁
2. 是否安装了 .NET Framework 4.5+
3. Python 和 Node.js 版本是否正确
4. 端口是否被其他程序占用
