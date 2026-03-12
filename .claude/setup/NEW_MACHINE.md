# 新机器复现环境

在新机器上启动 Claude Code 后，输入以下提示词（替换括号内的值）：

```
帮我复现开发环境。请执行以下步骤：
1. 用 wget 下载并执行 bootstrap 脚本：
   https_proxy=http://agent.baidu.com:8188 wget -qO /tmp/bootstrap.sh https://raw.githubusercontent.com/DongBaiYue/claude-skills/master/.claude/setup/bootstrap.sh
2. 运行：bash /tmp/bootstrap.sh <BCE_AK> <BCE_SK> <GITHUB_TOKEN>

BCE_AK: <你的 AK>
BCE_SK: <你的 SK>
GITHUB_TOKEN: <你的 token>
```

脚本会自动完成：安装 bcecmd → 下载环境包（128G）→ 解压 → 配置凭证。
