# RustDesk 自定义编译版

基于 [RustDesk](https://github.com/rustdesk/rustdesk) 的自定义编译版本，编译时内置自定义 ID 服务器配置。

> 详细的改动说明见 [CUSTOM.md](CUSTOM.md)。

## 功能特性

- ✅ 编译时内置 ID 服务器地址和公钥，客户端开箱即用
- ✅ 支持全平台编译（Windows / macOS / Linux / Android / iOS）
- ✅ 自动同步上游新版本并触发编译
- ✅ 用户可通过客户端设置覆盖内置值
- ✅ Android 包名 `com.rustdesk.app`，可与原版 RustDesk 共存

## 快速开始

### 1. 配置 GitHub Secrets

在仓库 **Settings → Secrets and variables → actions → Repository secrets** 中添加：

| Secret 名称 | 说明 | 示例 |
|---|---|---|
| `RENDEZVOUS_SERVER` | ID 服务器地址（含端口） | `your-server.com:21116` |
| `RS_PUB_KEY` | 服务器公钥（Base64 编码） | `your-base64-key=` |
| `API_SERVER` | API 服务器地址（可选） | `https://api.your-server.com` |

### 2. 触发编译

- **手动触发**：进入 Actions 页面 → 选择 "Sync Upstream Release" → 点击 "Run workflow"
- **自动触发**：每天自动检查上游新版本，发现新版本后自动合并并编译

### 3. 下载产物

从 **Releases** 页面下载安装包（不要从 Artifacts 下载，那里会被打包为 zip）：

- Windows: MSI 安装包 + EXE 安装包
- Linux: DEB / RPM 包
- Android: APK（aarch64）
- macOS: DMG（需在 `.build-config.yml` 中开启）

## 编译平台配置

默认只编译 Windows、Android、Linux 三个常用平台以加快编译速度。编辑 `.build-config.yml` 可开启更多平台：

```yaml
platforms:
  windows: true        # Windows x86_64 (MSI + EXE)
  windows_sciter: false # Windows Sciter 版 (32位兼容)
  macos: false          # macOS x86_64 + aarch64 (DMG)
  linux: true           # Linux x86_64 + aarch64 (DEB + RPM)
  linux_sciter: false   # Linux Sciter 版
  android: true         # Android aarch64 (APK)
  ios: false            # iOS（需要 Apple 开发者账号）
  appimage: false       # Linux AppImage
  flatpak: false        # Linux Flatpak
```

## 工作流说明

| 工作流 | 触发方式 | 功能 |
| --- | --- | --- |
| `build.yml` | 手动触发 / tag 推送 / sync 调用 | 自动获取上游版本号，编译并上传到 Releases |
| `sync-upstream.yml` | 每天自动 / 手动触发 | 检查上游新版本，按需合并代码，触发编译 |
| `flutter-build.yml` | 被 build.yml 调用 | 实际的编译逻辑（不直接触发） |

## 技术原理

使用 Rust `option_env!()` 宏在编译时从环境变量读取服务器配置，硬编码进二进制文件。

配置值存储在 GitHub Secrets 中，不会出现在源码、日志或编译产物中。

### 源码修改点

仅修改 `src/common.rs`，不修改子模块：

1. `global_init()` — 启动时从 `RENDEZVOUS_SERVER` 环境变量写入 `PROD_RENDEZVOUS_SERVER`
2. `get_key()` — 从 `RS_PUB_KEY` 环境变量读取默认公钥
3. `get_api_server_()` — 从 `API_SERVER` 环境变量读取 API 服务器地址
4. `check_software_update()` — 禁用官方更新检测

### Android 签名

CI 构建时如果没有配置签名密钥，会自动生成临时 keystore（每次不同，无法覆盖安装）。

如需固定签名（支持覆盖安装更新），在本地生成一次 keystore 并配置到 GitHub Secrets：

```bash
# 1. 本地生成 keystore（只需执行一次）
keytool -genkey -v -keystore release.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias rustdesk -storepass 你的密码 -keypass 你的密码 \
  -dname "CN=You, OU=Dev, O=You, L=City, ST=State, C=US"

# 2. 编码为 Base64
base64 -w 0 release.keystore   # Linux
# base64 release.keystore      # macOS
```

然后在 GitHub **Settings → Secrets → Repository secrets** 中配置：

| Secret 名称 | 值 |
|---|---|
| `ANDROID_SIGNING_KEY` | 上面输出的 Base64 字符串 |
| `ANDROID_ALIAS` | `rustdesk` |
| `ANDROID_KEY_STORE_PASSWORD` | 你设的密码 |
| `ANDROID_KEY_PASSWORD` | 你设的密码 |

## 上游同步

同步工作流每天自动检查上游仓库（`rustdesk/rustdesk`）的新版本：

- ✅ 无冲突 → 自动合并，触发编译，Release tag 与上游版本号一致
- ❌ 有冲突 → 自动创建 PR，手动解决后合并

手动触发 sync 或 build 时，已有的同版本 Release 会被自动覆盖。

上游仓库：<https://github.com/rustdesk/rustdesk>
