# RustDesk 自定义编译版 — 改动说明

本文件记录 fork 自 [rustdesk/rustdesk](https://github.com/rustdesk/rustdesk) 的所有自定义改动。

---

## 项目目标

编译内置自定义 ID 服务器配置的 RustDesk 客户端，支持全平台，自动同步上游新版本。

## 改动清单

### 1. 源码修改（`src/common.rs`）

| 位置 | 改动 | 作用 |
| --- | --- | --- |
| `global_init()` | 从 `RENDEZVOUS_SERVER` 环境变量写入 `PROD_RENDEZVOUS_SERVER` | 内置 ID 服务器地址 |
| `get_key()` | 从 `RS_PUB_KEY` 环境变量读取公钥 | 内置服务器公钥 |
| `get_api_server_()` | 从 `API_SERVER` 环境变量读取地址 | 内置 API 地址 |
| `check_software_update()` | 直接 return | 禁用官方更新检测 |
| `secure_tcp()` | 直接返回 `Ok(())` | 跳过握手，兼容 rustdesk-api |

使用 Rust `option_env!()` 宏在编译时读取环境变量，值来自 GitHub Secrets。

### 2. Android 修改

- **包名**：`com.carriez.flutter_hbb` → `com.rustdesk.app`（可与原版共存）
- **签名**：使用 `apksigner` 直接签名，支持自定义 keystore
- **防诈骗弹窗**：移除 `ScamWarningDialog` 的触发（自用版本不需要）

### 3. GitHub Actions 工作流

删除原有 11 个 workflow，新建 3 个 + 2 个辅助：

| 文件 | 作用 |
| --- | --- |
| `sync-upstream.yml` | 检查上游新版本，按需合并，触发编译 |
| `build.yml` | 编译入口，调用 flutter-build.yml |
| `flutter-build.yml` | 实际编译逻辑 |
| `bridge.yml` | flutter-rust-bridge 代码生成（辅助） |
| `third-party-RustDeskTempTopMostWindow.yml` | Windows 置顶窗口组件（辅助） |

**设计原则**：

- 平台控制：`.build-config.yml`
- Release 发布：`PUBLISH_RELEASE` 控制（默认 true）
- 产物去向：配置 `RELEASE_REPO` + `RELEASE_PAT` → 私有仓库；否则 → 当前仓库
- Actions Artifacts：不上传（仅 bridge-artifact 保留，编译依赖）

**sync-upstream 流程**：

```text
fetch upstream tags
       │
  上游 tag 的提交已在 HEAD 中？
      ╱              ╲
    是                否
     │                 │
  跳过           尝试合并到 custom-build
                    ╱          ╲
               成功             冲突
                │                │
         push + 触发 build    创建 upstream-merge-* 分支
                              自动解决部分冲突
                              创建 PR（含冲突详情）
```

**build.yml 流程**：

- `workflow_dispatch`：fetch upstream tags → 获取版本号 → 清理旧 Release → 编译
- tag push：从 tag 名解析版本号 → 编译

**私有 Release 仓库**：公开仓库享受免费 Actions 额度，产物推送到私有仓库。配置 `RELEASE_REPO` + `RELEASE_PAT` 即可。

### 4. 编译平台配置

`.build-config.yml` 控制编译哪些平台，默认精简为 Windows / Linux / Android。

---

## 上游合并注意事项

1. `src/common.rs` 的改动在函数内部，上游重构时可能需要手动合并
2. `.github/workflows/` 完全重写，上游 CI 变更不影响本 fork
3. `.gitignore` 中 `rustdesk` 已改为 `/rustdesk`，注意新增文件是否被误忽略
4. Kotlin 版本需与 AGP 兼容（当前 AGP 7.3.1 + Kotlin 1.9.10）

---

## 维护记录

| 日期 | 改动 |
| --- | --- |
| 2026-06-07 | 初始版本：基于 v1.4.7 创建，实现编译时注入、自动同步、全平台编译 |
| 2026-06-08 | 优化 workflow：sync 通过提交历史判断，build 自动获取版本号，Release tag 统一上游格式 |
| 2026-06-08 | 支持私有 Release 仓库，移除 Actions Artifacts 上传 |
| 2026-06-08 | 修复 Android 签名（改用 apksigner）、Kotlin 兼容性、gitignore 问题 |
| 2026-06-08 | 跳过 secure_tcp 握手，兼容 rustdesk-api；移除防诈骗弹窗 |
| 2026-06-09 | 重构 workflow：移除 UPLOAD_ARTIFACT/android-only，简化条件判断 |
| 2026-06-21 | 修复 sync-upstream：改进冲突处理（UD/DU/UU 分类处理），PR 描述动态生成冲突详情 |
| 2026-06-23 | sync-upstream 优化：workflow 文件保留本地版本，PR 描述含上游 diff；SYNC_PAT 用于创建 PR |
| 2026-06-23 | 全面优化 action：修复 version 输出 BUG、精确 git add、修复版本解析、避免重复触发 |
| 2026-06-24 | 修复 Windows ARM64 编译：artifact 名称添加平台后缀（x64/ARM64）匹配下载 |
| 2026-06-24 | 统一 Release 描述信息：所有平台（Windows/Android/Linux/Arch）使用相同的详细 body |
| 2026-06-24 | 系统审查并修复 workflow 问题：修复 --vram 传递给 ARM64、bridge cache key、模板注入、重复下载、并发控制等 |
| 2026-06-24 | 更新 RustDeskTempTopMostWindow 到支持 ARM64 的版本（ecd8d6a, 2026-06-18） |
| 2026-06-24 | 修复 bridge.yml：添加 Flutter 3.44 bridge 生成，支持 Windows ARM64 编译 |
| 2026-06-24 | 添加 .build-config.yml 中 windows_arm64 选项控制 Windows ARM64 编译（默认禁用） |
| 2026-07-09 | 修复 sync-upstream：合并 v1.4.9 失败（commit 退出 128）。根因为 libs/hbb_common 子模块 gitlink 冲突——CI 未检出子模块导致无法自动解决，且兜底复合 `git add ... libs/ ...` 因该冲突中止、索引残留未合并项。新增子模块 gitlink 冲突自动处理（采用上游 gitlink，已确认是前向更新无内部分叉），内容冲突改为显式暂存并标记人工复核，并以「逐个暂存所有遗留未合并项」的兜底循环替换脆弱复合 git add，确保 commit 前索引干净 |
