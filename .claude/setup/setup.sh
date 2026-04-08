#!/bin/bash
# 一键配置当前机器的凭证
# 用法：bash .claude/setup/setup.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CREDS="$SCRIPT_DIR/credentials"

if [ ! -f "$CREDS" ]; then
  echo "未找到凭证文件，请先执行："
  echo "  cp $SCRIPT_DIR/credentials.template $CREDS"
  echo "  然后填入 BCE_AK / BCE_SK / GITHUB_TOKEN"
  exit 1
fi

source "$CREDS"

# 配置 bcecmd
if command -v bcecmd &>/dev/null && [ -n "$BCE_AK" ] && [ -n "$BCE_SK" ]; then
  printf "${BCE_AK}\n${BCE_SK}\n\nnx\nbcebos.nx.nxjncloud.com:8080\nno\n\n\nno\n\n\n\n" | bcecmd -c 2>/dev/null
  echo "✓ bcecmd 已配置"
fi

# 配置 GitHub token
if [ -n "$GITHUB_TOKEN" ]; then
  git config --global credential.helper store
  echo "https://DongBaiYue:${GITHUB_TOKEN}@github.com" > ~/.git-credentials
  chmod 600 ~/.git-credentials
  echo "✓ GitHub token 已配置"
fi

# 配置 Git 用户
if [ -n "$GIT_USER_NAME" ] && [ -n "$GIT_USER_EMAIL" ]; then
  git config --global user.name "$GIT_USER_NAME"
  git config --global user.email "$GIT_USER_EMAIL"
  echo "✓ Git 用户已配置: $GIT_USER_NAME <$GIT_USER_EMAIL>"
fi

echo "完成，当前机器凭证配置就绪。"
