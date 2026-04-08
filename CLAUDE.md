# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概述

这是 Claude Code / Ducc 配置仓库，包含：
- **Rules** - 始终加载的规则和速查命令
- **Skills** - 按需触发的复杂任务流程
- **Memory** - 详细参考文档（由 rules 索引）

## 目录结构

```
.claude/
├── rules/                    # 始终加载的规则
│   ├── commands.md           # 常用命令速查
│   └── reference-index.md    # 指向 memory/ 的索引
├── skills/                   # 按需触发的 skills
│   └── <skill-name>/SKILL.md
└── setup/                    # 环境配置脚本

memory/                       # 详细参考文档
├── paddlepaddle.md           # PaddlePaddle 构建/架构
└── eb5.md                    # EB5 XPU 训练
```

**Rules vs Skills:**
- Rule: 始终在上下文中，适合速查、索引
- Skill: 按描述触发，适合多步骤任务

## Rule 结构

```yaml
---
name: rule-name
description: 规则说明
---

# Markdown 内容
```

## Skill 结构

```
.claude/skills/<skill-name>/
├── SKILL.md (必需)          # YAML frontmatter + Markdown 指令
├── scripts/ (可选)          # 可执行 Python 代码
├── references/ (可选)       # 按需加载的文档
└── assets/ (可选)           # 模板、图标等
```

**SKILL.md 格式：**
```yaml
---
name: skill-name
description: 触发条件及功能说明
allowed-tools: Bash(git:*), Read, ...  # 可选的工具限制
---

# Markdown 格式的 skill 指令
```

**渐进式加载：** Skills 采用三级加载：metadata（始终加载）→ SKILL.md body（触发时加载）→ bundled resources（按需加载）。SKILL.md 建议控制在 500 行以内。

## 已有 Skills

| Skill | 用途 |
|-------|------|
| `bcecmd-file-migrate` | 通过 bcecmd 跨机器迁移文件 |
| `ku-doc-manage` | 百度知识库文档管理（13 个 API 端点）|
| `pr-create` | 创建格式规范的 GitHub Pull Request |
| `skill-creator` | 创建、修改和评估 Claude skills |

## 环境配置

**新机器一键复现：**
```bash
bash .claude/setup/bootstrap.sh <BCE_AK> <BCE_SK> [GITHUB_TOKEN]
```

**当前机器配置：**
```bash
bash .claude/setup/setup.sh
```


## 关键约定

- **认证方式：** ku-doc-manage 使用 TOKEN（24h 过期），失败则回退到 AK/SK；pr-create 使用 `GH_TOKEN` 环境变量
- **默认远程：** pr-create 默认使用 `dongbaiyue` 作为 GitHub remote
- **BOS bucket：** bcecmd-file-migrate 使用 `nx-yongqiang` bucket
- **压缩策略：** bcecmd-file-migrate 根据目录大小选择不同的打包策略
