<<<<<<< HEAD
# RustDesk 自定义编译版
=======
<p align="center">
  <img src="res/logo-header.svg" alt="RustDesk - Your remote desktop"><br>
  <a href="#raw-steps-to-build">Build</a> •
  <a href="#how-to-build-with-docker">Docker</a> •
  <a href="#file-structure">Structure</a> •
  <a href="#screenshots">Screenshots</a><br>
  [<a href="docs/README-UA.md">Українська</a>] | [<a href="docs/README-CS.md">česky</a>] | [<a href="docs/README-ZH.md">中文</a>] | [<a href="docs/README-HU.md">Magyar</a>] | [<a href="docs/README-ES.md">Español</a>] | [<a href="docs/README-FA.md">فارسی</a>] | [<a href="docs/README-FR.md">Français</a>] | [<a href="docs/README-DE.md">Deutsch</a>] | [<a href="docs/README-PL.md">Polski</a>] | [<a href="docs/README-ID.md">Indonesian</a>] | [<a href="docs/README-FI.md">Suomi</a>] | [<a href="docs/README-ML.md">മലയാളം</a>] | [<a href="docs/README-JP.md">日本語</a>] | [<a href="docs/README-NL.md">Nederlands</a>] | [<a href="docs/README-IT.md">Italiano</a>] | [<a href="docs/README-RU.md">Русский</a>] | [<a href="docs/README-PTBR.md">Português (Brasil)</a>] | [<a href="docs/README-EO.md">Esperanto</a>] | [<a href="docs/README-KR.md">한국어</a>] | [<a href="docs/README-AR.md">العربي</a>] | [<a href="docs/README-VN.md">Tiếng Việt</a>] | [<a href="docs/README-DA.md">Dansk</a>] | [<a href="docs/README-GR.md">Ελληνικά</a>] | [<a href="docs/README-TR.md">Türkçe</a>] | [<a href="docs/README-NO.md">Norsk</a>] | [<a href="docs/README-RO.md">Română</a>]<br>
  <b>We need your help to translate this README, <a href="https://github.com/rustdesk/rustdesk/tree/master/src/lang">RustDesk UI</a> and <a href="https://github.com/rustdesk/doc.rustdesk.com">RustDesk Doc</a> to your native language</b>
</p>
>>>>>>> 1.5.0

基于 [RustDesk](https://github.com/rustdesk/rustdesk) 的自定义编译版本，编译时内置自定义 ID 服务器配置，自动同步上游新版本。

> 详细的改动说明见 [CUSTOM.md](CUSTOM.md)。

## 一、快速开始

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
| `SYNC_PAT` | Classic PAT，用于创建 PR（需 `repo` scope） | 可选 |

> ID 和 Key 必须同时填写，否则会出现 key 不匹配。都不填则等同于官方客户端。
>
> 未配置私有仓库时，产物发布到当前仓库的 Releases。

### 2. 触发编译

- **自动触发**：每天 UTC 03:23（北京时间 11:23）检查上游新版本，有更新则自动合并并编译
- **手动触发**：Actions → Sync Upstream Release → Run workflow（或直接触发 Build RustDesk）
- **PR 合并触发**：解决冲突后合并 PR 时，commit 消息包含 `[build]` 即可自动编译

### 3. 下载产物

从 Releases 页面下载安装包（配置了私有仓库则去私有仓库的 Releases）：

- Windows: MSI + EXE
- Linux: DEB（x86_64 / aarch64）+ RPM（x86_64）
- Android: APK（aarch64）

<<<<<<< HEAD
## 二、编译平台配置
=======
Desktop versions use Flutter or Sciter (deprecated) for GUI. This tutorial is for Sciter only, since it is easier and more friendly to start. Check out our [CI](https://github.com/rustdesk/rustdesk/blob/master/.github/workflows/flutter-build.yml) for building the Flutter version.
>>>>>>> 1.5.0

编辑 `.build-config.yml` 控制编译哪些平台：

<<<<<<< HEAD
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
=======
[Windows](https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.win/x64/sciter.dll) |
[Linux](https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.lnx/x64/libsciter-gtk.so) |
[macOS](https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.osx/libsciter.dylib)

## Raw Steps to build

- Prepare your Rust development env and C++ build env

- Install [vcpkg](https://github.com/microsoft/vcpkg), and set `VCPKG_ROOT` env variable correctly

  - Windows: vcpkg install libvpx:x64-windows-static libyuv:x64-windows-static opus:x64-windows-static aom:x64-windows-static
  - Linux/macOS: vcpkg install libvpx libyuv opus aom

- run `cargo run`

## [Build](https://rustdesk.com/docs/en/dev/build/)

## How to Build on Linux

### Ubuntu 18 (Debian 10)

```sh
sudo apt install -y zip g++ gcc git curl wget nasm yasm libgtk-3-dev clang libxcb-randr0-dev libxdo-dev \
        libxfixes-dev libxcb-shape0-dev libxcb-xfixes0-dev libasound2-dev libpulse-dev cmake make \
        libclang-dev ninja-build libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
>>>>>>> 1.5.0
```

## 三、工作流说明

<<<<<<< HEAD
| 工作流 | 触发方式 | 功能 |
| --- | --- | --- |
| `sync-upstream.yml` | 每天自动 / 手动 | 检查上游新版本，按需合并代码，触发编译 |
| `build.yml` | tag 推送 / sync 调用 | 获取版本号，编译并发布到 Releases |
| `flutter-build.yml` | 被 build.yml 调用 | 实际编译逻辑（不直接触发） |

## 四、上游同步

每天自动检查上游仓库（[rustdesk/rustdesk](https://github.com/rustdesk/rustdesk)）的新版本：

- 无冲突 → 自动合并，触发编译
- 有冲突 → 自动创建 PR，手动解决后合并
- 已是最新 → 跳过，不触发编译

手动触发时，已有的同版本 Release 会被自动覆盖。

## 五、参考内容

### 1. 生成 Android 签名密钥

```bash
# 1. 生成 keystore（只需执行一次）
keytool -genkey -v -keystore release.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias rustdesk -storepass 你的密码 -keypass 你的密码 \
  -dname "CN=RustDesk, OU=Dev, O=RustDesk, L=Unknown, ST=Unknown, C=US"

# 2. 编码为 Base64
base64 -w 0 release.keystore   # Linux
# base64 release.keystore      # macOS
=======
```sh
sudo zypper install gcc-c++ git curl wget nasm yasm gcc gtk3-devel clang libxcb-devel libXfixes-devel cmake alsa-lib-devel gstreamer-devel gstreamer-plugins-base-devel xdotool-devel
>>>>>>> 1.5.0
```

将输出的 Base64 字符串填入 `ANDROID_SIGNING_KEY`，别名填 `rustdesk`，密码填你设的值。

<<<<<<< HEAD
### 2. 私有 Release 仓库
=======
```sh
sudo yum -y install gcc-c++ git curl wget nasm yasm gcc gtk3-devel clang libxcb-devel libxdo-devel libXfixes-devel pulseaudio-libs-devel cmake alsa-lib-devel gstreamer1-devel gstreamer1-plugins-base-devel
```
>>>>>>> 1.5.0

公开仓库享受免费 Actions 额度，但 Releases 对所有人可见，存在泄露风险。

1\. 创建私有仓库

GitHub 上新建一个 private 仓库（如 `rustdesk-releases`），创建时勾选 **Initialize this repository with a README**[^1]。

[^1]: 仓库不能为空，否则 Release 创建会失败。

2\. 生成 PAT

GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token：

- Token name：随意（如 `rustdesk-release`）
- Expiration：选 1 年
- Repository access：选 `Only select repositories` → 选刚建的私有仓库
- Permissions → Repository permissions → **Contents**：`Read and write`

3\. 配置 Secret

在公开仓库 Settings → Secrets → Repository secrets 中添加：

| Secret 名称 | 值 |
| --- | --- |
| `RELEASE_REPO` | 私有仓库名（如 `inkss/rustdesk-releases`） |
| `RELEASE_PAT` | 上一步复制的 token |

配置后，编译产物会推送到私有仓库的 Releases，当前仓库不再有产物。

### 3. PAT 汇总

本项目需要两个 PAT，创建方式相同（GitHub → Settings → Developer settings → Personal access tokens）：

| Secret | 用途 | 推荐类型 | 权限 | 必填 |
| --- | --- | --- | --- | --- |
| `RELEASE_PAT` | 推送编译产物到私有仓库 | Fine-grained | 选私有仓库 → Contents: `Read and write` | 配置私有仓库时必填 |
| `REPO_TOKEN` | 上游同步时创建 PR | Classic | 勾选 `repo` scope | 可选（未配置时用 GITHUB_TOKEN） |

<<<<<<< HEAD
### 4. rustdesk-api 兼容
=======
```sh
target/debug/rustdesk
```

Or, if you're running a release executable:

```sh
target/release/rustdesk
```

Please ensure that you run these commands from the root of the RustDesk repository, or the application may not find the required resources. Also note that other cargo subcommands such as `install` or `run` are not currently supported via this method as they would install or run the program inside the container instead of the host.

## File Structure

- **[libs/hbb_common](https://github.com/rustdesk/rustdesk/tree/master/libs/hbb_common)**: video codec, config, tcp/udp wrapper, and some other utility functions shared with the server
- **[libs/base](https://github.com/rustdesk/rustdesk/tree/master/libs/base)**: protobuf, fs functions for file transfer, keyboard and platform code used only by this app
- **[libs/scrap](https://github.com/rustdesk/rustdesk/tree/master/libs/scrap)**: screen capture
- **[libs/enigo](https://github.com/rustdesk/rustdesk/tree/master/libs/enigo)**: platform specific keyboard/mouse control
- **[libs/clipboard](https://github.com/rustdesk/rustdesk/tree/master/libs/clipboard)**: file copy and paste implementation for Windows, Linux, macOS.
- **[src/ui](https://github.com/rustdesk/rustdesk/tree/master/src/ui)**: obsolete Sciter UI (deprecated)
- **[src/server](https://github.com/rustdesk/rustdesk/tree/master/src/server)**: audio/clipboard/input/video services, and network connections
- **[src/client.rs](https://github.com/rustdesk/rustdesk/tree/master/src/client.rs)**: start a peer connection
- **[src/rendezvous_mediator.rs](https://github.com/rustdesk/rustdesk/tree/master/src/rendezvous_mediator.rs)**: Communicate with [rustdesk-server](https://github.com/rustdesk/rustdesk-server), wait for remote direct (TCP hole punching) or relayed connection
- **[src/platform](https://github.com/rustdesk/rustdesk/tree/master/src/platform)**: platform specific code
- **[flutter](https://github.com/rustdesk/rustdesk/tree/master/flutter)**: Flutter code for desktop and mobile

## Screenshots

![Connection Manager](https://github.com/rustdesk/rustdesk/assets/28412477/db82d4e7-c4bc-4823-8e6f-6af7eadf7651)

![Connected to a Windows PC](https://github.com/rustdesk/rustdesk/assets/28412477/9baa91e9-3362-4d06-aa1a-7518edcbd7ea)

![File Transfer](https://github.com/rustdesk/rustdesk/assets/28412477/39511ad3-aa9a-4f8c-8947-1cce286a46ad)

![TCP Tunneling](https://github.com/rustdesk/rustdesk/assets/28412477/78e8708f-e87e-4570-8373-1360033ea6c5)
>>>>>>> 1.5.0

本版本兼容 [lejianwen/rustdesk-api](https://github.com/lejianwen/rustdesk-api)，跳过了 `secure_tcp` 握手，登录 API 账户后不会出现连接超时。
