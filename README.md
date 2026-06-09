# RustDesk 自定义编译版

基于 [RustDesk](https://github.com/rustdesk/rustdesk) 的自定义编译版本，编译时内置自定义 ID 服务器配置。

> 详细的改动说明见 [CUSTOM.md](CUSTOM.md)。

## 功能特性

- ✅ 编译时内置 ID 服务器地址和公钥，客户端开箱即用
- ✅ 支持全平台编译（Windows / Linux / Android）
- ✅ 自动同步上游新版本并触发编译
- ✅ 用户可通过客户端设置覆盖内置值
- ✅ Android 包名 `com.rustdesk.app`，可与原版 RustDesk 共存
- ✅ 支持私有 Release 仓库，公开仓库享受免费 Actions 额度

## 快速开始

### 1. 配置 GitHub Secrets

在仓库 **Settings → Secrets and variables → actions → Repository secrets** 中添加：

**服务器配置（ID 和 Key 必须同时填写）：**

| Secret 名称 | 说明 | 必填 |
| --- | --- | --- |
| `RENDEZVOUS_SERVER` | ID 服务器地址（含端口） | ✅ |
| `RS_PUB_KEY` | 服务器公钥（Base64 编码） | ✅ |
| `API_SERVER` | API 服务器地址 | 可选 |

> ID 和 Key 必须同时填写，否则会出现 key 不匹配。都不填则等同于官方客户端。

**Android 签名（可选，支持覆盖安装）：**

| Secret 名称 | 说明 |
| --- | --- |
| `ANDROID_SIGNING_KEY` | Base64 编码的 keystore 文件 |
| `ANDROID_ALIAS` | keystore 别名（如 `rustdesk`） |
| `ANDROID_KEY_STORE_PASSWORD` | keystore 密码 |
| `ANDROID_KEY_PASSWORD` | key 密码 |

**私有 Release 仓库（可选）：**

| Secret 名称 | 说明 |
| --- | --- |
| `RELEASE_REPO` | 私有仓库名（如 `inkss/rustdesk-releases`） |
| `RELEASE_PAT` | Fine-grained PAT，需对私有仓库有 Contents 读写权限 |

不配置私有仓库时，产物发布到当前仓库的 Releases。

### 2. 触发编译

- **手动触发**：进入 Actions 页面 → 选择 "Sync Upstream Release" → 点击 "Run workflow"
- **自动触发**：每天 UTC 03:23（北京时间 11:23）自动检查上游新版本

### 3. 下载产物

从 **Releases** 页面下载安装包（配置了私有仓库则去私有仓库的 Releases 页面）：

- Windows: MSI 安装包 + EXE 安装包
- Linux: DEB / RPM 包
- Android: APK（aarch64）

## 编译平台配置

编辑 `.build-config.yml` 控制编译哪些平台：

```yaml
platforms:
  windows: true        # Windows x86_64 (MSI + EXE)
  windows_sciter: false
  macos: false
  linux: true          # Linux x86_64 + aarch64 (DEB + RPM)
  linux_sciter: false
  android: true        # Android aarch64 (APK)
  ios: false
  appimage: false
  flatpak: false
```

## 工作流说明

| 工作流 | 触发方式 | 功能 |
| --- | --- | --- |
| `sync-upstream.yml` | 每天自动 / 手动触发 | 检查上游新版本，按需合并代码，触发编译 |
| `build.yml` | tag 推送 / sync 调用 | 自动获取上游版本号，编译并上传到 Releases |
| `flutter-build.yml` | 被 build.yml 调用 | 实际的编译逻辑（不直接触发） |

## 上游同步

同步工作流每天自动检查上游仓库（`rustdesk/rustdesk`）的新版本：

- ✅ 无冲突 → 自动合并，触发编译，Release tag 与上游版本号一致
- ❌ 有冲突 → 自动创建 PR，手动解决后合并

手动触发 sync 或 build 时，已有的同版本 Release 会被自动覆盖。

上游仓库：<https://github.com/rustdesk/rustdesk>
