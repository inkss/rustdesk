#!/usr/bin/env python3
"""检查 Android Kotlin 文件的 package 声明是否残留上游包名。

背景
----
本 fork 将 Android 包名从 ``com.carriez.flutter_hbb`` 改为 ``com.rustdesk.app``，
源码目录也随之重命名。上游新增的 Kotlin 文件（如 v1.5.1 的 ``Document*.kt``）
在合并后会落到 ``com/rustdesk/app/`` 目录下，但文件内的 ``package`` 声明仍是
旧包名，导致 Kotlin 报 ``Unresolved reference`` —— 而这个错误要等 Rust 交叉编译
（约 40 分钟）之后才会在 gradle 阶段暴露。

在编译前跑一遍本脚本，可在 1 分钟内发现问题，避免浪费整轮编译。

用法
----
    python3 .github/scripts/check_android_package.py [项目根目录]

退出码：0 = 通过；1 = 发现残留包名。

注意
----
只匹配 ``package`` 声明里的旧包名，不要求 package 与目录一致：
上游存在 ``package hbb`` 这类历史遗留（Kotlin 不强制 package 匹配目录），
它们能正常编译，不应被当错误处理。
"""

from __future__ import annotations

import os
import re
import sys

# 本 fork 使用的当前包名
CURRENT_PACKAGE = "com.rustdesk.app"
# 上游原始包名的特征片段，命中即为漏改
LEGACY_MARKERS = ("carriez", "flutter_hbb")

# 相对项目根目录的 Android 源码路径
ANDROID_ROOT = os.path.join("flutter", "android")

# 匹配行首的 package 声明（允许多余空白）
PACKAGE_RE = re.compile(r"(?m)^[ \t]*package[ \t]+([\w.]+)")


def scan(root: str) -> tuple[int, list[tuple[str, str, int]]]:
    """扫描 Android 目录下所有 .kt 文件。

    :param root: 项目根目录
    :return: (扫描的 .kt 文件数, 问题列表)，问题列表元素为
             (文件相对路径, package 声明原文, 行号)
    """
    base = os.path.join(root, ANDROID_ROOT)
    if not os.path.isdir(base):
        return 0, []

    total = 0
    problems: list[tuple[str, str, int]] = []

    for dirpath, _dirnames, filenames in os.walk(base):
        for name in filenames:
            if not name.endswith(".kt"):
                continue
            full = os.path.join(dirpath, name)
            total += 1
            with open(full, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            for match in PACKAGE_RE.finditer(text):
                pkg = match.group(1)
                if any(marker in pkg for marker in LEGACY_MARKERS):
                    line = text.count("\n", 0, match.start()) + 1
                    problems.append(
                        (os.path.relpath(full, root), match.group(0).strip(), line)
                    )

    return total, problems


def main(argv: list[str]) -> int:
    root = argv[1] if len(argv) > 1 else os.getcwd()
    total, problems = scan(root)

    print(f"scanned {total} kotlin file(s) under {ANDROID_ROOT}")

    for path, decl, line in problems:
        print(
            f"::error file={path},line={line}::{decl} "
            f"—— 包名未随 fork 改写为 {CURRENT_PACKAGE}"
        )

    if problems:
        print(f"\n❌ 发现 {len(problems)} 处残留包名，请修正后重跑")
        return 1

    print(f"✅ Android 包名检查通过（当前包名 {CURRENT_PACKAGE}）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
