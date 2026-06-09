# RustDesk 自定义编译版 — 改动说明

本文件记录 fork 自 [rustdesk/rustdesk](https://github.com/rustdesk/rustdesk) 的所有自定义改动，供开发者和 AI 工具快速对齐上下文。

---

## 项目目标

编译一个内置自定义 ID 服务器配置的 RustDesk 客户端，支持全平台，自动同步上游新版本。

## 分支策略

- **工作分支**: `custom-build`（基于上游 release tag 创建）
- **上游同步**: 每天自动检查上游正式发布版本 tag，合并后触发编译

---

## 改动清单

### 1. 源码修改（`src/common.rs`）

| 位置 | 改动 | 作用 |
| --- | --- | --- |
| `global_init()` | 从 `RENDEZVOUS_SERVER` 环境变量写入 `PROD_RENDEZVOUS_SERVER` | 编译时内置 ID 服务器地址 |
| `get_key()` | 从 `RS_PUB_KEY` 环境变量读取默认公钥 | 编译时内置服务器公钥 |
| `get_api_server_()` | 从 `API_SERVER` 环境变量读取 API 服务器 | 编译时内置 API 地址 |
| `check_software_update()` | 直接 return，跳过更新检测 | 禁用官方更新检测 |
| `secure_tcp()` | 直接返回 `Ok(())`，跳过握手 | 解决 rustdesk-api 登录后连接超时 |

**原理**: 使用 Rust `option_env!()` 宏在编译时读取环境变量。值来自 GitHub Secrets，不进入源码。

**优先级**: 用户在客户端设置中的配置 > 编译时内置值 > 原始默认值（用户可覆盖）。

### 2. Android 包名修改

将 `com.carriez.flutter_hbb` 改为 `com.rustdesk.app`，使自定义版可与原版 RustDesk 共存安装。

| 文件 | 改动 |
| --- | --- |
| `flutter/android/app/build.gradle` | `applicationId` |
| `flutter/android/app/src/main/AndroidManifest.xml` | `package` 属性 + 所有组件引用 |
| `flutter/android/app/src/debug/AndroidManifest.xml` | `package` 属性 |
| `flutter/android/app/src/profile/AndroidManifest.xml` | `package` 属性 |
| `flutter/android/app/src/main/kotlin/com/rustdesk/app/*.kt` | 12 个 Kotlin 文件的 `package` 声明 |
| `flutter/android/app/src/main/kotlin/ffi.kt` | `import` 语句 |
| `Cargo.toml` | macOS bundle `identifier` |

### 3. Android 签名配置

`flutter/android/app/build.gradle` 中启用 v1+v2 签名方案。CI 使用 `apksigner` 直接签名，不依赖第三方 Action。

支持两种模式：

- 未配置 `ANDROID_SIGNING_KEY` → debug 签名（每次不同，不能覆盖安装）
- 配置了 `ANDROID_SIGNING_KEY` → 固定签名（支持覆盖安装）

### 4. 移除 Android 防诈骗弹窗

`flutter/lib/mobile/pages/server_page.dart` 中移除 `ScamWarningDialog` 的两处触发。自用版本不需要此安全提示。

### 5. GitHub Actions 工作流

删除原有 11 个 workflow，新建 3 个 + 2 个辅助：

| 文件 | 作用 | 触发方式 |
| --- | --- | --- |
| `sync-upstream.yml` | 检查上游新版本，按需合并代码，触发编译 | 每天自动 / 手动 |
| `build.yml` | 编译入口，自动解析版本号，调用 flutter-build.yml | tag 推送 / sync 调用 |
| `flutter-build.yml` | 实际编译逻辑（被调用） | workflow_call |
| `bridge.yml` | flutter-rust-bridge 代码生成（辅助） | workflow_call |
| `third-party-RustDeskTempTopMostWindow.yml` | Windows 置顶窗口组件（辅助） | workflow_call |

#### 设计原则

- **平台控制**: 只看 `.build-config.yml`
- **Release 发布**: 由 `PUBLISH_RELEASE` 控制（默认 true）
- **产物去向**: 配置 `RELEASE_REPO` + `RELEASE_PAT` → 私有仓库；否则 → 当前仓库
- **Actions Artifacts**: 不上传（仅 bridge-artifact 保留，编译依赖，无敏感信息）

#### sync-upstream 流程

```text
fetch upstream tags
       │
  上游最新 tag 的提交已在 HEAD 中？
      ╱              ╲
    是                否
     │                 │
  跳过合并           合并代码 → push
      ╲              ╱
       ▼            ▼
   触发 build.yml（不传版本号）
```

- 通过 `git merge-base --is-ancestor` 检查提交历史，不依赖本地 tag 是否存在
- Release tag 统一使用上游格式（如 `1.4.7`）

#### build.yml 流程

- `workflow_dispatch` 时：fetch upstream tags，自动获取最新版本号，清理旧 Release/tag 后编译
- tag push 时：从 tag 名解析版本号，直接编译
- 无手动版本号输入，版本号始终跟随上游

#### 私有 Release 仓库配置

1. 创建 private 仓库（如 `inkss/rustdesk-releases`）
2. 生成 Fine-grained PAT：Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Repository access：选 `Only select repositories` → 选私有仓库
   - Permissions → Repository permissions → Contents：`Read and write`
3. 在公开仓库 Settings → Secrets → Repository secrets 中添加：
   - `RELEASE_PAT`：PAT 值
   - `RELEASE_REPO`：私有仓库名

### 6. 编译平台配置

`.build-config.yml` 控制编译哪些平台：

```yaml
platforms:
  windows: true        # Windows x86_64
  windows_sciter: false
  macos: false
  linux: true          # Linux x86_64 + aarch64
  linux_sciter: false
  android: true        # Android aarch64
  ios: false
  appimage: false
  flatpak: false
```

### 7. 环境变量（GitHub Secrets）

**服务器配置（ID 和 Key 必须同时填写）：**

| Secret | 说明 | 必填 |
| --- | --- | --- |
| `RENDEZVOUS_SERVER` | ID 服务器地址 | ✅ |
| `RS_PUB_KEY` | 服务器公钥（Base64） | ✅ |
| `API_SERVER` | API 服务器地址 | 可选 |

**Android 签名（可选）：**

| Secret | 说明 |
| --- | --- |
| `ANDROID_SIGNING_KEY` | Base64 编码的 keystore |
| `ANDROID_ALIAS` | 别名 |
| `ANDROID_KEY_STORE_PASSWORD` | keystore 密码 |
| `ANDROID_KEY_PASSWORD` | key 密码 |

**私有 Release（可选）：**

| Secret | 说明 |
| --- | --- |
| `RELEASE_REPO` | 私有仓库名 |
| `RELEASE_PAT` | Fine-grained PAT |

---

## 未修改的部分

- `libs/hbb_common/` 子模块 — 完全未动
- 协议层、加密、网络逻辑 — 无修改
- Flutter 前端代码（Dart） — 仅移除防诈骗弹窗
- 其他平台编译逻辑 — 仅添加环境变量注入

---

## 上游合并注意事项

1. `src/common.rs` 的改动在函数内部，上游重构函数签名时可能需要手动合并
2. `.github/workflows/` 目录完全重写，上游 CI 变更不影响本 fork
3. `.gitignore` 中 `rustdesk` 已改为 `/rustdesk`，新增上游文件时注意检查是否被误忽略
4. `flutter-build.yml` 基于上游原始版本改造，上游大版本更新时可能需要重新同步
5. Kotlin 版本需与 AGP 兼容（当前 AGP 7.3.1 + Kotlin 1.9.10）

---

## 维护记录

| 日期 | 改动 |
| --- | --- |
| 2026-06-07 | 初始版本：基于 v1.4.7 创建，实现编译时注入、自动同步、全平台编译 |
| 2026-06-07 | Android 包名改为 `com.rustdesk.app`，启用 v1+v2+v3 签名 |
| 2026-06-07 | 新增 `.build-config.yml` 平台编译配置 |
| 2026-06-07 | 精简编译平台，只保留 windows/linux/android |
| 2026-06-07 | 禁用官方更新检测 |
| 2026-06-08 | 优化 workflow 版本管理：sync 通过提交历史判断，build 自动获取上游版本号 |
| 2026-06-08 | 修复 Kotlin 文件被 gitignore 忽略 |
| 2026-06-08 | 支持私有 Release 仓库 |
| 2026-06-08 | 分离 artifact 上传和 Release 发布，移除所有 upload-artifact 步骤 |
| 2026-06-08 | 修复 Android 签名：替换为 apksigner 直接签名 |
| 2026-06-08 | 修复 secure_tcp 超时：直接跳过握手，兼容 rustdesk-api |
| 2026-06-08 | 移除 Android 防诈骗弹窗 |
| 2026-06-08 | 重构 workflow：移除 UPLOAD_ARTIFACT/android-only，简化条件判断 |
