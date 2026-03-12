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

# 凭证从仓库 .claude/setup/credentials 读取，运行一次即可完成配置
bash <仓库根目录>/.claude/setup/setup.sh
```

---

## 迁移步骤

打包方式根据目录大小选择：
- **小目录**（几 GB 以内）：用 `-czf` 压缩，节省存储和传输带宽
- **大目录**（几十 GB 以上）：用 `-cf` 不压缩，省去 CPU 开销，速度快很多

**源机器：**
```bash
# 小目录：压缩打包
tar -czf project.tar.gz -C /root/workspace project
bcecmd bos cp ./project.tar.gz bos:/nx-yongqiang/personal/liuyi39/project.tar.gz

# 大目录：不压缩打包（推荐后台运行）
nohup bash -c '
  tar -cf /root/workspace/project.tar -C /root/workspace project \
  && bcecmd bos cp /root/workspace/project.tar bos:/nx-yongqiang/personal/liuyi39/project.tar \
  && echo "完成"
' > /tmp/migrate.log 2>&1 &
# 查看进度
watch -n 10 'ls -lh /root/workspace/project.tar'
```

**目标机器：**
```bash
# 下载
bcecmd bos cp bos:/nx-yongqiang/personal/liuyi39/project.tar.gz ./project.tar.gz

# 解压（压缩包用 -xzf，非压缩包用 -xf）
tar -xzf project.tar.gz -C /root/workspace/   # .tar.gz
tar -xf  project.tar    -C /root/workspace/   # .tar
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
