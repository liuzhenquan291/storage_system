@echo off
chcp 65001 >nul
title 打包仓储系统为 EXE

:: 检查是否安装了必要的工具

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║         仓储系统 EXE 打包工具                             ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: 检查是否安装了 7-Zip（用于创建自解压包）
if exist "C:\Program Files\7-Zip\7z.exe" (
    set "SEVENZIP=C:\Program Files\7-Zip\7z.exe"
) else if exist "C:\Program Files (x86)\7-Zip\7z.exe" (
    set "SEVENZIP=C:\Program Files (x86)\7-Zip\7z.exe"
) else (
    echo [WARNING] 未找到 7-Zip，将使用备用方案
    set SEVENZIP=
)

echo.
echo 请选择打包方式：
echo.
echo [1] 创建 ZIP 压缩包（推荐，简单通用）
echo [2] 创建自解压 EXE（需要 7-Zip）
echo [3] 生成 Inno Setup 脚本（专业安装包）
echo [4] 查看打包说明文档
echo.
set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" goto create_zip
if "%choice%"=="2" goto create_sfx
if "%choice%"=="3" goto create_inno_script
if "%choice%"=="4" goto show_help
goto end

:create_zip
echo.
echo [INFO] 正在创建 ZIP 压缩包...
echo.

:: 创建临时目录
set "BUILD_DIR=build_temp"
if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%
mkdir %BUILD_DIR%

:: 复制必要文件
echo 复制项目文件...
xcopy /s /i /q start.bat %BUILD_DIR%\
xcopy /s /i /q docker-compose.yml %BUILD_DIR%\
xcopy /s /i /q README.md %BUILD_DIR%\
xcopy /s /i /q 打包说明.md %BUILD_DIR%\
xcopy /s /i /q backend %BUILD_DIR%\backend\
xcopy /s /i /q frontend %BUILD_DIR%\frontend\
xcopy /s /i /q docker %BUILD_DIR%\docker\
xcopy /s /i /q scripts %BUILD_DIR%\scripts\

:: 使用 PowerShell 创建 ZIP
set "ZIP_NAME=仓储物资出入库动态管理系统_v1.0.0.zip"
echo 创建压缩包: %ZIP_NAME%

powershell -Command "Compress-Archive -Path '%BUILD_DIR%\*' -DestinationPath '%ZIP_NAME%' -Force"

:: 清理临时目录
rmdir /s /q %BUILD_DIR%

echo.
echo [SUCCESS] 压缩包已创建: %ZIP_NAME%
echo.
echo 使用说明：
echo 1. 解压 %ZIP_NAME%
echo 2. 确保已安装 Docker Desktop
echo 3. 双击运行 start.bat
echo.
pause
goto end

:create_sfx
if "%SEVENZIP%"=="" (
    echo.
    echo [ERROR] 未找到 7-Zip，无法创建自解压包
    echo 请先安装 7-Zip: https://www.7-zip.org/
    echo.
    pause
    goto end
)

echo.
echo [INFO] 正在创建自解压 EXE...
echo.

:: 创建临时目录
set "BUILD_DIR=build_temp"
if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%
mkdir %BUILD_DIR%

:: 复制必要文件
echo 复制项目文件...
xcopy /s /i /q start.bat %BUILD_DIR%\
xcopy /s /i /q docker-compose.yml %BUILD_DIR%\
xcopy /s /i /q README.md %BUILD_DIR%\
xcopy /s /i /q 打包说明.md %BUILD_DIR%\
xcopy /s /i /q backend %BUILD_DIR%\backend\
xcopy /s /i /q frontend %BUILD_DIR%\frontend\
xcopy /s /i /q docker %BUILD_DIR%\docker\
xcopy /s /i /q scripts %BUILD_DIR%\scripts\

:: 创建 7z 压缩包
set "SFX_NAME=仓储物资出入库动态管理系统_v1.0.0.exe"
echo 创建自解压程序: %SFX_NAME%

:: 创建 SFX 配置文件
echo ;!@Install@!UTF-8! > sfx_config.txt
echo Title="仓储物资出入库动态管理系统 v1.0.0" >> sfx_config.txt
echo BeginPrompt="欢迎使用仓储物资出入库动态管理系统\n\n本程序将解压系统文件到指定目录，然后您可以在该目录运行 start.bat 启动系统。\n\n是否继续？" >> sfx_config.txt
echo ExtractPathText="请选择解压目标文件夹" >> sfx_config.txt
echo ExtractDialogText="正在解压文件，请稍候..." >> sfx_config.txt
echo ExtractPath="%USERPROFILE%\WarehouseSystem" >> sfx_config.txt
echo RunProgram="start.bat" >> sfx_config.txt
echo ;!@InstallEnd@! >> sfx_config.txt

:: 使用 7-Zip 创建自解压包
"%SEVENZIP%" a -sfx7z.sfx -r -mhe=on -mx=9 "%SFX_NAME%" %BUILD_DIR%\* sfx_config.txt

:: 清理临时文件
rmdir /s /q %BUILD_DIR%
del sfx_config.txt

echo.
echo [SUCCESS] 自解压程序已创建: %SFX_NAME%
echo.
echo 使用说明：
echo 1. 双击运行 %SFX_NAME%
echo 2. 选择解压目录
echo 3. 解压后自动运行启动脚本
echo.
pause
goto end

:create_inno_script
echo.
echo [INFO] 正在生成 Inno Setup 脚本...
echo.

set "INNO_SCRIPT=仓储系统安装脚本.iss"

echo ; 仓储物资出入库动态管理系统安装脚本 > %INNO_SCRIPT%
echo ; 使用 Inno Setup 编译器编译 >> %INNO_SCRIPT%
echo. >> %INNO_SCRIPT%
echo [Setup] >> %INNO_SCRIPT%
echo AppName=仓储物资出入库动态管理系统 >> %INNO_SCRIPT%
echo AppVersion=1.0.0 >> %INNO_SCRIPT%
echo AppPublisher=仓储管理系统 >> %INNO_SCRIPT%
echo AppPublisherURL=http://localhost:3003 >> %INNO_SCRIPT%
echo DefaultDirName={autopf}\WarehouseSystem >> %INNO_SCRIPT%
echo DefaultGroupName=仓储管理系统 >> %INNO_SCRIPT%
echo OutputBaseFilename=仓储管理系统_v1.0.0_安装包 >> %INNO_SCRIPT%
echo OutputDir=.	 >> %INNO_SCRIPT%
echo Compression=lzma2 >> %INNO_SCRIPT%
echo SolidCompression=yes >> %INNO_SCRIPT%
echo SetupIconFile=.	 >> %INNO_SCRIPT%
echo WizardStyle=modern >> %INNO_SCRIPT%
echo PrivilegesRequired=admin >> %INNO_SCRIPT%
echo. >> %INNO_SCRIPT%
echo [Languages] >> %INNO_SCRIPT%
echo Name: "chinesesimplified"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl" >> %INNO_SCRIPT%
echo. >> %INNO_SCRIPT%
echo [Tasks] >> %INNO_SCRIPT%
echo Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked >> %INNO_SCRIPT%
echo. >> %INNO_SCRIPT%
echo [Files] >> %INNO_SCRIPT%
echo Source: "start.bat"; DestDir: "{app}"; Flags: ignoreversion >> %INNO_SCRIPT%
echo Source: "docker-compose.yml"; DestDir: "{app}"; Flags: ignoreversion >> %INNO_SCRIPT%
echo Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion >> %INNO_SCRIPT%
echo Source: "打包说明.md"; DestDir: "{app}"; Flags: ignoreversion >> %INNO_SCRIPT%
echo Source: "backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs >> %INNO_SCRIPT%
echo Source: "frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs >> %INNO_SCRIPT%
echo Source: "docker\*"; DestDir: "{app}\docker"; Flags: ignoreversion recursesubdirs createallsubdirs >> %INNO_SCRIPT%
echo Source: "scripts\*"; DestDir: "{app}\scripts"; Flags: ignoreversion recursesubdirs createallsubdirs >> %INNO_SCRIPT%
echo. >> %INNO_SCRIPT%
echo [Icons] >> %INNO_SCRIPT%
echo Name: "{group}\启动仓储系统"; Filename: "{app}\start.bat" >> %INNO_SCRIPT%
echo Name: "{group}\查看说明"; Filename: "{app}\README.md" >> %INNO_SCRIPT%
echo Name: "{group}\卸载仓储系统"; Filename: "{uninstallexe}" >> %INNO_SCRIPT%
echo Name: "{autodesktop}\仓储管理系统"; Filename: "{app}\start.bat"; Tasks: desktopicon >> %INNO_SCRIPT%
echo. >> %INNO_SCRIPT%
echo [Run] >> %INNO_SCRIPT%
echo Filename: "{app}\start.bat"; Description: "立即启动系统"; Flags: nowait postinstall skipifsilent >> %INNO_SCRIPT%
echo. >> %INNO_SCRIPT%
echo [UninstallDelete] >> %INNO_SCRIPT%
echo Type: filesandordirs; Name: "{app}" >> %INNO_SCRIPT%

echo.
echo [SUCCESS] Inno Setup 脚本已生成: %INNO_SCRIPT%
echo.
echo 下一步：
echo 1. 下载并安装 Inno Setup: https://jrsoftware.org/isinfo.php
echo 2. 打开 Inno Setup 编译器
echo 3. 选择 "Open"，打开 %INNO_SCRIPT%
echo 4. 点击 "Build" ^> "Compile"
echo 5. 生成的安装包在 OutputDir 目录中
echo.
pause
goto end

:show_help
start 打包说明.md
goto end

:end
