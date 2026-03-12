#!/bin/bash
# 新机器一键复现环境
# 用法：bash bootstrap.sh <BCE_AK> <BCE_SK> <GITHUB_TOKEN>

BCE_AK=$1
BCE_SK=$2
GITHUB_TOKEN=${3:-}

if [ -z "$BCE_AK" ] || [ -z "$BCE_SK" ]; then
  echo "用法：bash bootstrap.sh <BCE_AK> <BCE_SK> [GITHUB_TOKEN]"
  exit 1
fi

set -e

# 1. 安装 bcecmd（如未安装）
if ! command -v bcecmd &>/dev/null; then
  echo ">>> 安装 bcecmd..."
  export http_proxy=http://agent.baidu.com:8188 && export https_proxy=$http_proxy
  wget -q https://doc.bce.baidu.com/bos-optimization/linux-bcecmd-0.5.10.zip
  unzip -q linux-bcecmd-0.5.10.zip
  ln -sf $(pwd)/linux-bcecmd-0.5.10/bcecmd /usr/sbin/bcecmd
fi

# 2. 配置 bcecmd
echo ">>> 配置 bcecmd..."
printf "${BCE_AK}\n${BCE_SK}\n\nnx\nbcebos.nx.nxjncloud.com:8080\nno\n\n\nno\n\n\n\n" | bcecmd -c 2>/dev/null
echo "✓ bcecmd 配置完成"

# 3. 下载环境包
TARGET=/root/paddlejob/workspace/env_run
mkdir -p $TARGET
echo ">>> 从 BOS 下载环境包（128G，需要一段时间）..."
nohup bcecmd bos cp bos:/nx-yongqiang/personal/liuyi39/liuyi39.tar \
  $TARGET/liuyi39.tar > /tmp/bootstrap_download.log 2>&1 &
DOWNLOAD_PID=$!
echo "下载 PID: $DOWNLOAD_PID，日志：tail -f /tmp/bootstrap_download.log"

# 等待下载完成
wait $DOWNLOAD_PID
echo "✓ 下载完成"

# 4. 解压
echo ">>> 解压中..."
tar -xf $TARGET/liuyi39.tar -C $TARGET/
echo "✓ 解压完成"

# 5. 写入 credentials 并初始化
CREDS=$TARGET/liuyi39/claude-skills/.claude/setup/credentials
cat > $CREDS << CREDS_EOF
BCE_AK=${BCE_AK}
BCE_SK=${BCE_SK}
GITHUB_TOKEN=${GITHUB_TOKEN}
CREDS_EOF
bash $TARGET/liuyi39/claude-skills/.claude/setup/setup.sh
echo "✓ 凭证配置完成"

echo ""
echo "环境复现完成！"
