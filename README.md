# Claude Skills

存放 Claude Code / Ducc 自定义 Skill 和 Rule 文件的仓库。

## 目录结构

```
.claude/
├── rules/                    # 始终加载的规则/速查
│   ├── commands.md           # 常用命令速查
│   └── reference-index.md    # 文档索引
├── skills/                   # 按需触发的 skills
│   └── <skill-name>/SKILL.md
└── setup/                    # 环境配置脚本

memory/                       # 详细参考文档
├── paddlepaddle.md           # PaddlePaddle 构建/架构
└── eb5.md                    # EB5 XPU 训练
```

## Rules vs Skills

| 类型 | 加载方式 | 用途 |
|------|----------|------|
| Rule | 始终加载 | 常用命令速查、文档索引 |
| Skill | 按描述触发 | 多步骤复杂任务 |

## 使用方式

将本仓库克隆到你的项目目录下，或在 Claude Code 的 settings 中配置 skills 路径。
