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
4. Kotlin 版本需与 AGP 兼容（跟随上游配套版本，1.5.0 为 AGP 8.10.1 + Kotlin 2.1.21）
5. **上游 release tag 位于与 master 分叉的发布分支**（1.4.9 与 1.5.0 都是 master 的祖先，但 1.5.0 并不包含 1.4.9 之后的 master 提交）。因此合并 tag 时，git 可能把「上游移动过的代码块」与「fork 仍保留的旧位置副本」同时留下却不报冲突（v1.5.0 的 `login.dart` 就因此重复声明）。合并后需留意这类静默重复：以「与上游 1.x 文件对比」为准，重复块直接删掉
6. 上游升级 vcpkg 版本后，需同步 `flutter-build.yml` 的 `VCPKG_COMMIT_ID`，否则 `vcpkg.json` 里的端口版本在旧版本库中找不到
7. **`GITHUB_TOKEN`（GitHub App 令牌）有三条限制**：① 无 `workflows` 权限（`permissions` 里不存在该键）→ 推送含 workflow 文件变更的 ref 会被拒绝，靠 sync 流程"提交前清空 `.github/workflows/` 并只还原本地备份"规避；② 由它发起的 API 调用不会创建新的 workflow run → `workflow_dispatch` 触发编译不会生效；③ 由它推送的 commit 不触发 push 事件的工作流。**需要在仓库 Secrets 配置 `SYNC_PAT`（Classic PAT，勾选 `repo` + `workflow`）**，才能让"无冲突自动合并 → 自动编译"真正闭环；未配置时 sync 仍可完成合并与建 PR，但自动触发编译会失败并输出告警（不会静默）
8. `actions/github-script` 的输入名是 `github-token`，写成 `token:` 会被静默忽略（不报错），导致 PAT 实际未生效

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
| 2026-07-09 | 修复 v1.4.9 编译失败（actions run 28995435596）：`src/` 已升至上游 1.4.9，但 `libs/hbb_common` 子模块指针仍停在旧提交 `387603f4`，缺少 `ControlledContext`、`OPTION_ALLOW_SCOPE_VIOLATION_*`、proto `controlled_context` 等符号。将子模块前移到上游 1.4.9 配套的 `7e1c392c`（纯前向更新，无内部分叉），提交 `c4e271282` 并打 `1.4.9` tag 触发重编 |
| 2026-09-27 | 修复 sync-upstream：合并 v1.5.0 连续 3 天失败（09-25/26/27 的 push 均被拒：`refusing to allow a GitHub App to create or update workflow .github/workflows/update-webpki-roots.yml without workflows permission`）。根因是上游新增的 workflow 文件不产生冲突，被 `git add .github/workflows/` 带入合并提交，而 `SYNC_PAT` 未配置、回退的 `GITHUB_TOKEN` 无 workflow 写权限（`permissions` 不存在 `workflows` 键，只有带 workflow scope 的 PAT 才有）。改为提交前 `git rm -r -f --cached .github/workflows/` 清空索引并只还原本地备份集，保证合并提交不携带 workflow 变更 |
| 2026-09-27 | 合并上游 v1.5.0（PR #7，86 个冲突文件）：`src/lang/*` 采用上游 1.5.0 译文（上游删除的插件条目不再复活）；core 采用上游改动（PunchSlot 透传、ID 白名单、文件传输目录校验、peer id 校验等）；保留本地定制——`src/common.rs` 编译期注入（RENDEZVOUS_SERVER/RS_PUB_KEY/API_SERVER）、Android 包名 `com.rustdesk.app`、`README.md`/`CLAUDE.md` 本地版本、`.gitignore` 合并两侧；版本号统一升至 1.5.0 |
| 2026-09-27 | 修复 v1.5.0 编译：①`flutter-build.yml` 的 `VCPKG_COMMIT_ID` 仍是 2025.08.27，而 1.5.0 的 `vcpkg.json` 需要 libjpeg-turbo 3.2.0 / pkgconf 3.0.3 / vcpkg-cmake-config 2026-07-21，旧版本库没有这些条目，三平台 `Install vcpkg dependencies` 失败——改用上游的 2026.07.29（`9e593bb1`）；②Linux ARM64 运行环境自带 CMake 3.31，新版 vcpkg 的 SPDX 脚本要求 CMake 4.3+（`string(JSON ... STRING_ENCODE)`），参照上游增加 pip 安装 `cmake==4.3.0` 的步骤（`VCPKG_CMAKE_VERSION`） |
| 2026-09-27 | 修复 v1.5.0 编译：`flutter/lib/common/widgets/login.dart` 中 `_OidcProviderBranding` 被声明两次，三平台 Flutter 构建报 `already declared in this scope`。原因是上游 1.5.0 把该代码块移动了位置，而 fork 仍保留旧位置，git 三向合并把两份都留下（不报冲突）。删除重复块，与上游 1.5.0 一致 |
| 2026-09-27 | v1.5.0 全平台编译成功（actions run 36325873327：Windows 48m / Linux x86_64 33m / Linux aarch64 31m / Android 31m），产物已发布到私有仓库 `inkss/rustdesk-releases` 的 `1.5.0` Release（10 个 assets） |
| 2026-09-27 | 修复 sync-upstream 凭据问题：①`actions/github-script` 的入参名是 `github-token`，原 `token:` 被静默忽略，`REPO_TOKEN/SYNC_PAT` 从未生效；②`Trigger build` 未传凭据，而 `GITHUB_TOKEN` 发起的 `workflow_dispatch` 不会创建运行，无冲突合并后会"看似成功但不编译"。现改为显式传 `github-token`（建 PR 仍用 `GITHUB_TOKEN` 保证可用，触发编译优先 PAT），失败时 `core.warning` + job summary 明确告警而非静默。同时删除已合并的临时分支 `upstream-merge-1.5.0/1.4.9/1.4.8` |
