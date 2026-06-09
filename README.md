# RustDesk 自定义编译版

基于 [RustDesk](https://github.com/rustdesk/rustdesk) 的自定义编译版本，编译时内置自定义 ID 服务器配置，自动同步上游新版本。

> 详细的改动说明见 [CUSTOM.md](CUSTOM.md)。

## 快速开始

### 1. 配置 GitHub Secrets

在仓库 **Settings → Secrets and variables → actions → Repository secrets** 中添加：

| Secret 名称 | 说明 | 必填 |
| --- | --- | --- |
| `RENDEZVOUS_SERVER` | ID 服务器地址（含端口，如 `your-server.com:21116`） | ✅ |
| `RS_PUB_KEY` | 服务器公钥（Base64 编码，位于服务器 `id_ed25519.pub`） | ✅ |
| `API_SERVER` | API 服务器地址（如 `https://api.your-server.com`） | 可选 |
| `ANDROID_SIGNING_KEY` | Base64 编码的 keystore 文件 | 可选 |
| `ANDROID_ALIAS` | keystore 别名 | 可选 |
| `ANDROID_KEY_STORE_PASSWORD` | keystore 密码 | 可选 |
| `ANDROID_KEY_PASSWORD` | key 密码 | 可选 |
| `RELEASE_REPO` | 私有仓库名（如 `inkss/rustdesk-releases`） | 可选 |
| `RELEASE_PAT` | Fine-grained PAT，对私有仓库有 Contents 读写权限 | 可选 |

> ID 和 Key 必须同时填写，否则会出现 key 不匹配。都不填则等同于官方客户端。
>
> 未配置私有仓库时，产物发布到当前仓库的 Releases。

#### 生成 Android 签名密钥

```bash
# 1. 生成 keystore（只需执行一次）
keytool -genkey -v -keystore release.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias rustdesk -storepass 你的密码 -keypass 你的密码 \
  -dname "CN=RustDesk, OU=Dev, O=RustDesk, L=Unknown, ST=Unknown, C=US"

# 2. 编码为 Base64
base64 -w 0 release.keystore   # Linux
# base64 release.keystore      # macOS
```

将输出的 Base64 字符串填入 `ANDROID_SIGNING_KEY`，别名填 `rustdesk`，密码填你设的值。未配置时使用 debug 签名（每次不同，不能覆盖安装）。

#### rustdesk-api 兼容

本版本兼容 [lejianwen/rustdesk-api](https://github.com/lejianwen/rustdesk-api)，跳过了 `secure_tcp` 握手，登录 API 账户后不会出现连接超时。详见 [CUSTOM.md](CUSTOM.md)。

### 2. 触发编译

- **自动触发**：每天 UTC 03:23（北京时间 11:23）检查上游新版本，有更新则自动合并并编译
- **手动触发**：Actions → Sync Upstream Release → Run workflow（或直接触发 Build RustDesk）

### 3. 下载产物

从 Releases 页面下载安装包（配置了私有仓库则去私有仓库的 Releases）：

- Windows: MSI + EXE
- Linux: DEB（x86_64 / aarch64）+ RPM（x86_64）
- Android: APK（aarch64）

## 编译平台配置

编辑 `.build-config.yml` 控制编译哪些平台：

```yaml
platforms:
  windows: true        # Windows x86_64
  linux: true          # Linux x86_64 + aarch64
  android: true        # Android aarch64
  macos: false
  ios: false
  windows_sciter: false
  linux_sciter: false
  appimage: false
  flatpak: false
```

## 工作流说明

| 工作流 | 触发方式 | 功能 |
| --- | --- | --- |
| `sync-upstream.yml` | 每天自动 / 手动 | 检查上游新版本，按需合并代码，触发编译 |
| `build.yml` | tag 推送 / sync 调用 | 获取版本号，编译并发布到 Releases |
| `flutter-build.yml` | 被 build.yml 调用 | 实际编译逻辑（不直接触发） |

## 上游同步

每天自动检查上游仓库（[rustdesk/rustdesk](https://github.com/rustdesk/rustdesk)）的新版本：

- 无冲突 → 自动合并，触发编译
- 有冲突 → 自动创建 PR，手动解决后合并
- 已是最新 → 跳过，不触发编译

手动触发时，已有的同版本 Release 会被自动覆盖。
