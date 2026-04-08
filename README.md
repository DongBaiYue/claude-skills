# Claude Skills

Claude Code / Ducc 配置仓库，包含 Skills、Rules 和参考文档。

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/DongBaiYue/claude-skills.git

# 2. 复制到你的项目根目录
cp -r claude-skills/.claude your-project/
cp -r claude-skills/memory your-project/
cp claude-skills/.cursorrules your-project/

# 3. 在项目目录启动 Claude Code
cd your-project && claude
```

`.claude/` 在项目根目录会自动加载。

**可选：配置凭证**（用于 bcecmd-file-migrate、pr-create）
```bash
cd your-project/.claude/setup
cp credentials.template credentials
# 编辑 credentials 填入 BCE_AK、BCE_SK、GITHUB_TOKEN、GIT_USER_NAME、GIT_USER_EMAIL
bash setup.sh
```

## 目录结构

```
.cursorrules                   # Agent 行为准则

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
