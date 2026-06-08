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

仅修改 1 个文件，新增约 15 行代码，不修改子模块。

| 位置 | 改动 | 作用 |
|---|---|---|
| `global_init()` | 从 `RENDEZVOUS_SERVER` 环境变量写入 `PROD_RENDEZVOUS_SERVER` | 编译时内置 ID 服务器地址 |
| `get_key()` | 从 `RS_PUB_KEY` 环境变量读取默认公钥 | 编译时内置服务器公钥 |
| `get_api_server_()` | 从 `API_SERVER` 环境变量读取 API 服务器 | 编译时内置 API 地址 |
| `check_software_update()` | 直接 return，跳过更新检测 | 禁用官方更新检测 |

**原理**: 使用 Rust `option_env!()` 宏在编译时读取环境变量。值来自 GitHub Secrets，不进入源码。

**优先级**: 用户在客户端设置中的配置 > 编译时内置值 > 原始默认值（用户可覆盖）。

### 2. Android 包名修改

将 `com.carriez.flutter_hbb` 改为 `com.rustdesk.app`，使自定义版可与原版 RustDesk 共存安装。

| 文件 | 改动 |
|---|---|
| `flutter/android/app/build.gradle` | `applicationId` |
| `flutter/android/app/src/main/AndroidManifest.xml` | `package` 属性 + 所有组件引用 |
| `flutter/android/app/src/debug/AndroidManifest.xml` | `package` 属性 |
| `flutter/android/app/src/profile/AndroidManifest.xml` | `package` 属性 |
| `flutter/android/app/src/main/kotlin/com/rustdesk/app/*.kt` | 12 个 Kotlin 文件的 `package` 声明（目录从 `carriez/flutter_hbb` 移动到 `rustdesk/app`） |
| `flutter/android/app/src/main/kotlin/ffi.kt` | `import` 语句 |
| `Cargo.toml` | macOS bundle `identifier` |

**注意**: 上游不会修改包名，合并时不会冲突。

### 3. Android 签名配置

`flutter/android/app/build.gradle` 中启用 v1+v2 签名方案，兼容 Android 高版本。

```groovy
signingConfigs {
  release {
    v1SigningEnabled true
    v2SigningEnabled true
    v3SigningEnabled true
  }
}
```

CI 构建时自动生成 keystore 签名（无需配置 `ANDROID_SIGNING_KEY`），也支持用户提供自定义签名密钥。

### 4. GitHub Actions 工作流

删除原有 11 个 workflow，新建 3 个：

| 文件 | 作用 | 触发方式 |
|---|---|---|
| `build.yml` | 编译入口，自动解析版本号，调用 flutter-build.yml | 手动 / tag 推送 / sync 调用 |
| `sync-upstream.yml` | 检查上游新版本，按需合并代码，触发编译 | 每天自动 / 手动 |
| `flutter-build.yml` | 实际编译逻辑（被调用），版本号动态获取 | workflow_call |

辅助 workflow（内部依赖，用户无需关注）：
- `bridge.yml` — flutter-rust-bridge 代码生成
- `third-party-RustDeskTempTopMostWindow.yml` — Windows 置顶窗口组件

#### sync-upstream.yml 流程

```
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
- 不创建 `v*` 前缀 tag，Release tag 统一使用上游格式（如 `1.4.7`）

#### build.yml 流程

- `workflow_dispatch` 时：fetch upstream tags，自动获取最新版本号，清理旧 Release/tag 后编译
- tag push 时：从 tag 名解析版本号，直接编译
- 无手动版本号输入，版本号始终跟随上游

### 5. 编译平台配置

`.build-config.yml` 控制编译哪些平台，默认精简为常用平台以加快速度：

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

### 6. 环境变量（GitHub Secrets）

| Secret | 说明 | 必填 |
|---|---|---|
| `RENDEZVOUS_SERVER` | ID 服务器地址（如 `your-server.com:21116`） | ✅ |
| `RS_PUB_KEY` | 服务器公钥（Base64） | ✅ |
| `API_SERVER` | API 服务器地址 | 可选 |

---

## 未修改的部分

- `libs/hbb_common/` 子模块 — 完全未动，保持与上游一致
- 协议层、加密、网络逻辑 — 无任何修改
- Flutter 前端代码（Dart） — 无修改
- 其他平台编译逻辑 — 仅添加环境变量注入，不改构建流程

---

## 上游合并注意事项

1. 本 fork 的改动集中在 `src/common.rs`（小范围）和 CI/CD 文件（独立目录）
2. 上游更新不会修改包名，Kotlin 文件合并无冲突
3. `src/common.rs` 的改动在函数内部，上游重构函数签名时可能需要手动合并
4. `.github/workflows/` 目录完全重写，上游 CI 变更不影响本 fork
5. `flutter-build.yml` 基于上游原始版本改造，上游大版本更新时可能需要重新同步
6. `.gitignore` 中 `rustdesk` 已改为 `/rustdesk`，新增上游文件时注意检查是否被误忽略

---

## 维护记录

| 日期 | 改动 |
|---|---|
| 2026-06-07 | 初始版本：基于 v1.4.7 创建，实现编译时注入、自动同步、全平台编译 |
| 2026-06-07 | Android 包名改为 `com.rustdesk.app`，启用 v1+v2+v3 签名 |
| 2026-06-07 | 新增 `.build-config.yml` 平台编译配置，默认精简为 Windows/Android/Linux |
| 2026-06-07 | Release 描述优化，包含版本号和上游版本信息 |
| 2026-06-07 | 移除 `build-rustdesk-web`，修复 `publish_unsigned` 平台跳过时的依赖问题 |
| 2026-06-07 | 精简编译平台：移除 windows-sciter/macos/ios/linux-sciter/appimage/flatpak/publish_unsigned，只保留 windows/linux/android |
| 2026-06-07 | 禁用官方更新检测（check_software_update 直接 return） |
| 2026-06-07 | 添加 Android 专用编译 workflow（build-android.yml） |
| 2026-06-08 | 优化 workflow 版本管理：sync 通过提交历史判断是否需要合并，build 自动从上游获取版本号，Release tag 统一上游格式（无 v 前缀），手动触发时自动覆盖旧 Release |
| 2026-06-08 | 修复 Android Kotlin 文件被 gitignore 忽略：`rustdesk` 规则改为 `/rustdesk`，提交 `com.rustdesk.app` 下 12 个 Kotlin 源文件 |
