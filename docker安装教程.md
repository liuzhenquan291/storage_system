# Windows 系统 Docker 安装与国内镜像配置完整指南

## 一、系统要求与版本选择

### 系统要求

- **Windows 10**：64位，版本 1903（Build 18362）或更高
- **Windows 11**：所有版本
- **内存**：至少 4GB RAM（建议 8GB+）
- **存储**：至少 20GB 可用空间
- **虚拟化**：BIOS/UEFI 中启用虚拟化（VT-x/AMD-V）

### 版本区别

| 版本类型                         | 虚拟化后端                       | 特点                           |
| -------------------------------- | -------------------------------- | ------------------------------ |
| **Windows 家庭版**               | **仅支持 WSL 2**                 | 不支持 Hyper-V，必须安装 WSL 2 |
| **Windows 专业版/企业版/教育版** | **WSL 2（推荐）** 或 **Hyper-V** | 两者可选，WSL 2 性能更优       |

------

## 二、国内下载地址（避免官网慢速）

### Docker Desktop 安装包

| 来源                 | 地址                                                         | 说明                     |
| -------------------- | ------------------------------------------------------------ | ------------------------ |
| **阿里云镜像站**     | `https://mirrors.aliyun.com/docker-toolbox/windows/docker-desktop/` | 推荐，下载速度快         |
| **天翼云盘（备用）** | `https://cloud.189.cn/t/QV3IRjRz6bmi`密码：`uof4`            | 包含最新版安装包         |
| **微软商店**         | 搜索 "Docker Desktop"                                        | 自动更新，但下载可能较慢 |

**注意**：根据你的 CPU 架构选择：

- **Intel/AMD 芯片** → 下载 **x86_64 (amd64)** 版本
- **ARM 芯片（部分 Surface）** → 下载 **ARM** 版本

------

## 三、安装步骤（按系统版本）

### 方案 A：Windows 家庭版（必须使用 WSL 2）

#### 步骤 1：安装 WSL 2

1. **以管理员身份打开 PowerShell**
2. 执行以下命令：`# 启用 WSL 功能 dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart # 启用虚拟机平台 dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart`
3. **重启电脑**
4. 重启后，设置 WSL 2 为默认版本：`wsl --set-default-version 2`
5. （可选）安装 Linux 发行版：打开 Microsoft Store，搜索安装 **Ubuntu** 或 **Debian**首次启动时设置用户名和密码

#### 步骤 2：安装 Docker Desktop

1. 从上述国内地址下载 `Docker Desktop Installer.exe`
2. 双击运行安装程序
3. 在安装向导中，**务必勾选**：✅ `Use WSL 2 instead of Hyper-V`（使用 WSL 2 后端）✅ `Create a desktop shortcut`（创建桌面快捷方式）
4. 点击安装，完成后按提示重启电脑

------

### 方案 B：Windows 专业版/企业版/教育版（推荐 WSL 2）

#### 推荐：WSL 2 方案（性能更优）

1. 按照 **方案 A 的步骤 1** 安装配置 WSL 2
2. 按照 **方案 A 的步骤 2** 安装 Docker Desktop，勾选 `Use WSL 2 instead of Hyper-V`

#### 备选：Hyper-V 方案（传统方式）

1. 打开“控制面板” → “程序” → “启用或关闭 Windows 功能”
2. 勾选：✅ `Hyper-V`✅ `Windows 虚拟机监控程序平台`
3. 点击确定，重启电脑
4. 安装 Docker Desktop，**不勾选** `Use WSL 2 instead of Hyper-V`

------

## 四、配置国内镜像源（加速下载）

### 方法一：通过 Docker Desktop 图形界面（推荐）

1. **打开设置**在任务栏右下角找到 Docker 鲸鱼图标**右键点击** → 选择 **Settings**（设置）
2. **配置镜像源**左侧菜单选择 **Docker Engine**在右侧编辑框中，找到或添加 `"registry-mirrors"`字段填入以下国内镜像地址（选2-3个即可）：

### 推荐镜像源地址（2025-2026年稳定可用）

| 镜像源           | 地址                                 | 特点                |
| ---------------- | ------------------------------------ | ------------------- |
| **DaoCloud**     | `https://docker.m.daocloud.io`       | 老牌稳定，推荐首选  |
| **网易云**       | `https://hub-mirror.c.163.com`       | 免费，无需登录      |
| **中科大**       | `https://docker.mirrors.ustc.edu.cn` | 学术用途，稳定      |
| **腾讯云**       | `https://mirror.ccs.tencentyun.com`  | 腾讯云用户内网更优  |
| **官方中国镜像** | `https://registry.docker-cn.com`     | Docker 官方中国镜像 |

**配置示例**（直接复制使用）：

```
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://hub-mirror.c.163.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "features": {
    "buildkit": true
  }
}
```

1. **应用配置**点击右下角 **Apply & Restart**Docker 会自动重启使配置生效

### 方法二：手动编辑配置文件

如果图形界面配置失败：

1. 打开文件：`C:\ProgramData\docker\config\daemon.json`
2. 以管理员身份用记事本编辑，添加上述配置
3. 保存后，右键 Docker 图标选择 **Restart**

------

## 五、验证安装与配置

### 验证 Docker 安装

打开 PowerShell，执行：

```
# 查看版本
docker --version

# 查看详细信息
docker info
```

### 验证镜像源配置

```
# 查看镜像源是否生效
docker info | findstr /i "Registry Mirrors"
```

输出应显示你配置的镜像地址。

### 测试镜像下载

```
# 测试拉取速度
docker pull nginx:latest
```

------

## 六、常见问题解决

### 1. WSL 2 安装卡住

- **检查虚拟化**：任务管理器 → 性能 → 虚拟化显示“已启用”
- **手动下载内核**：下载 [WSL 2 内核更新包](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi)离线安装
- **重置 WSL**：`wsl --shutdown`→ `wsl --unregister Ubuntu`→ 重新安装

### 2. Docker 启动失败

- **以管理员身份运行** Docker Desktop
- **关闭防火墙/杀毒软件** 临时测试
- **检查服务**：服务中确保 `Docker Desktop Service`正在运行

### 3. 镜像源不生效

- **JSON 格式检查**：确保没有多余逗号、引号
- **重启 Docker**：配置修改后必须重启
- **更换镜像源**：某个源可能暂时不可用，换其他源尝试

------

## 七、安装后优化

### 1. 修改镜像存储位置（避免 C 盘爆满）

```
# 停止 Docker
wsl --shutdown

# 导出 WSL 发行版
wsl --export Ubuntu D:\docker\ubuntu.tar

# 注销原发行版
wsl --unregister Ubuntu

# 导入到新位置
wsl --import Ubuntu D:\docker\ubuntu D:\docker\ubuntu.tar --version 2
```

### 2. 配置资源限制

- 打开 Docker Desktop Settings → Resources
- 调整 CPU、内存、磁盘限制，避免资源占用过高

按照以上步骤，你可以在 Windows 系统上顺利完成 Docker 的安装和配置，享受快速的镜像下载体验。如果在安装过程中遇到具体问题，可以随时进一步询问。
QQ: 450891406
