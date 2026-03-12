---
name: bcecmd-file-migrate
description: |
  使用 bcecmd 通过百度内网 BOS（bucket: nx-yongqiang）跨机器迁移文件的操作指南。
  当用户需要在机器之间传文件、上传/下载 BOS 文件、或提到 bcecmd 时触发本 skill。
---

# 使用 bcecmd 跨机器迁移文件

核心流程：**打包 → 上传 BOS → 下载 → 解压**。

直接批量上传文件会导致可执行权限丢失，所以始终用 tar 打包再传。

---

## 前置：安装并配置 bcecmd

需要迁移文件的机器都要装好 bcecmd。先检查是否已安装：

```bash
bcecmd -v
```

如果已有输出则跳过安装，直接到迁移步骤。否则执行：

```bash
export http_proxy=http://agent.baidu.com:8188 && export https_proxy=$http_proxy
wget https://doc.bce.baidu.com/bos-optimization/linux-bcecmd-0.5.10.zip
unzip linux-bcecmd-0.5.10.zip
ln -s $(pwd)/linux-bcecmd-0.5.10/bcecmd /usr/sbin/bcecmd

# 配置 AK/SK（替换为你自己的，只需配置一次）
printf "<YOUR_AK>\n<YOUR_SK>\n\nnx\nbcebos.nx.nxjncloud.com:8080\nno\n\n\nno\n\n\n\n" | bcecmd -c
```

---

## 迁移步骤

**源机器：**
```bash
# 1. 打包目录（以 /root/workspace/project 为例）
tar -czf project.tar.gz -C /root/workspace project

# 2. 上传
bcecmd bos cp ./project.tar.gz bos:/nx-yongqiang/personal/liuyi39/project.tar.gz
```

**目标机器：**
```bash
# 1. 下载
bcecmd bos cp bos:/nx-yongqiang/personal/liuyi39/project.tar.gz ./project.tar.gz

# 2. 解压
tar -xzf project.tar.gz -C /root/workspace/
```

---

## 分享文件给其他人（对方无需安装 bcecmd）

生成签名链接，对方用 curl 下载即可：

```bash
# 源机器：生成 24h 有效链接
bcecmd bos gen_signed_url bos:/nx-yongqiang/personal/liuyi39/project.tar.gz -e86400

# 对方机器：curl 下载
curl -o project.tar.gz "<上面生成的链接>"
```

---

## 参考

- bcecmd 使用文档：https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/pKzJfZczuc/1m_s72d2qB/tSu4BEc3nw-vGs
- bcecmd 命令参考：https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/XlJgy-Ki9w/xt7S40_t30/BB3icLrjeBwiTB
