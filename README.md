# RustDesk 自定义编译版

基于 [RustDesk](https://github.com/rustdesk/rustdesk) 的自定义编译版本，编译时内置自定义 ID 服务器配置。

## 功能特性

- ✅ 编译时内置 ID 服务器地址和公钥，客户端开箱即用
- ✅ 支持全平台编译（Windows / macOS / Linux / Android / iOS）
- ✅ 自动同步上游新版本并触发编译
- ✅ 用户可通过客户端设置覆盖内置值

## 快速开始

### 1. 配置 GitHub Secrets

在仓库 **Settings → Secrets and variables → actions** 中添加以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|---|---|---|
| `RENDEZVOUS_SERVER` | ID 服务器地址（含端口） | `your-server.com:21116` |
| `RS_PUB_KEY` | 服务器公钥（Base64 编码） | `your-base64-key=` |
| `API_SERVER` | API 服务器地址（可选） | `https://api.your-server.com` |

### 2. 触发编译

编译有两种触发方式：

- **手动触发**：进入 Actions 页面 → 选择 "Build RustDesk" → 点击 "Run workflow"（首次使用）
- **自动触发**：每天自动检查上游新版本，发现新版本后自动合并并编译

### 3. 下载产物

编译完成后，在 Actions → 对应 run → Artifacts 中下载各平台安装包：

- Windows: `rustdesk-*-windows-x86_64`
- macOS: `rustdesk-*-macos-x86_64` / `rustdesk-*-macos-aarch64`
- Linux: `rustdesk-*-linux-x86_64` / `rustdesk-*-linux-aarch64`
- Android: `rustdesk-*-android-arm64.apk` / `rustdesk-*-android-armv7.apk`
- iOS: `rustdesk-*-ios`

## 工作流说明

| 工作流 | 触发方式 | 功能 |
|---|---|---|
| `build.yml` | 手动触发 / tag 推送 | 全平台编译，上传产物 |
| `sync-upstream.yml` | 每天自动 / 手动触发 | 检查上游新版本，合并代码，触发编译 |
| `flutter-build.yml` | 被 build.yml 调用 | 实际的编译逻辑（不直接触发） |

## 技术原理

使用 Rust `option_env!()` 宏在编译时从环境变量读取服务器配置，硬编码进二进制文件。

配置值存储在 GitHub Secrets 中，不会出现在源码、日志或编译产物中。

### 源码修改点

仅修改 3 处，对上游代码侵入最小：

1. `libs/hbb_common/src/config.rs` — `RS_PUB_KEY` 使用 `option_env!()` 提供编译时默认值
2. `libs/hbb_common/src/config.rs` — `PROD_RENDEZVOUS_SERVER` 从环境变量初始化
3. `src/common.rs` — `get_api_server_()` 添加 `API_SERVER` 环境变量检查

## 可选：签名相关 Secrets

如需对安装包进行代码签名，可配置以下 Secrets：

| Secret 名称 | 说明 |
|---|---|
| `ANDROID_SIGNING_KEY` | Android APK 签名密钥（Base64） |
| `ANDROID_ALIAS` | Android 签名别名 |
| `ANDROID_KEY_STORE_PASSWORD` | Android Keystore 密码 |
| `ANDROID_KEY_PASSWORD` | Android 密钥密码 |
| `MACOS_P12_BASE64` | macOS 签名证书（Base64） |

## 上游同步

同步工作流每天自动检查上游仓库（`rustdesk/rustdesk`）的新版本：

- ✅ 无冲突 → 自动合并，创建 tag，触发编译
- ❌ 有冲突 → 自动创建 PR，手动解决后合并

上游仓库：<https://github.com/rustdesk/rustdesk>
