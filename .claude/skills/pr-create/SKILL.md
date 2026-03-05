---
name: pr-create
description: 创建格式规范的 GitHub Pull Request。当用户需要创建 PR、提交变更审查，或输入 /pr 时触发。
allowed-tools: Bash(git:*), Bash(gh:*), Read, Grep, Glob
---

# 创建 Pull Request

创建 GitHub PR。

## PR 标题格式

### 摘要规则

- 使用祈使句现在时：用 "Add" 而非 "Added"
- 首字母大写
- 结尾不加句号

### 硬件平台前缀

若变更涉及非 GPU 的特定硬件平台，在标题最前面加对应前缀（GPU 无需标注）：

- XPU：`[XPU]`
- ROCm：`[ROCm]`
- 其他平台类推

示例：`[XPU][Fix] moe_permute_kernel: add return_expert_indices and expert_indices params`

## 环境配置

在执行主流程前，确认以下环境已就绪。

### 1. gh CLI 安装与认证

检查 `gh` 是否安装：

```bash
gh --version
```

若未安装，优先尝试直接下载二进制

```bash
export http_proxy=http://agent.baidu.com:8188 && export https_proxy=$http_proxy
curl -fsSL https://github.com/cli/cli/releases/download/v2.47.0/gh_2.47.0_linux_amd64.tar.gz -o /tmp/gh.tar.gz
tar -xzf /tmp/gh.tar.gz -C /tmp
cp /tmp/gh_2.47.0_linux_amd64/bin/gh /usr/local/bin/gh
gh --version
```

由于机器可能多人公用，避免使用 `gh auth login`（会写入全局配置影响他人），改用环境变量临时传入 token，仅对当前 session 生效：

```bash
export GH_TOKEN=<your_token>
```

`gh` CLI 会自动识别 `GH_TOKEN`，session 结束后自动失效，不影响其他用户。

### 2. git 用户配置

确认 git 用户信息已配置：

```bash
git config user.name
git config user.email
```

若未配置，执行（替换为自己的信息）：

```bash
git config --global user.name "liuyi39"
git config --global user.email "liuyi39@baidu.com"
```

### 3. 网络访问

若无法访问 GitHub，尝试配置代理：

```bash
# 推荐（更稳定）
export http_proxy=http://agent.baidu.com:8188 && export https_proxy=$http_proxy

# 备选
export http_proxy=http://agent.baidu.com:8891 && export https_proxy=$http_proxy
export no_proxy=localhost,bj.bcebos.com,su.bcebos.com,pypi.tuna.tsinghua.edu.cn,paddle-ci.gz.bcebos.com
```

推送和 `gh` 命令执行时均需确保代理已设置。

---

## 执行步骤

1. **检查当前状态**：

   ```bash
   git status          # 查看变更文件列表
   git diff            # 查看未暂存的具体变更
   git diff --staged   # 查看已暂存的变更
   ```

   若 `git status` 显示无任何变更，终止流程并提示用户当前没有需要提交的内容。

   若当前处于 `main`、`master` 或 `develop` 等公共分支，应先创建新分支再继续。根据变更内容分析，按 `<type>/<description>` 格式建议分支名。
   ```bash
   git checkout -b <type>/<short-description>
   # 示例：git checkout -b feat/add-user-login
   ```

2. **分析变更**，确定以下内容：
   - 类型：这是什么类型的变更（参考步骤1的 type 表）？
   - 摘要：变更做了什么？
   - 范围：涉及哪些文件或模块？

   逐一列出变更文件，向用户确认哪些文件需要纳入本次提交，哪些不需要（如临时调试文件、本地配置等）。未确认前不要执行 `git add`。

3. **提交变更**：

   根据步骤2的分析结果，按以下格式自动生成 commit message，并展示给用户确认后再执行：

   ```
   [<Type>] <scope>: <short summary of all changes>
   ```

   其中：
   - `Type`：首字母大写，如 `Fix`、`Feat`、`Enhancement`、`Docs`、`Refactor`
   - `scope`：变更涉及的模块或文件名
   - 摘要保持简洁，单行即可；若变更点较多可附加 bullet，但不强制

   示例（简洁单行）：
   ```
   [Fix] moe_permute_kernel: add return_expert_indices and expert_indices params
   ```

   示例（含 bullet）：
   ```
   [Enhancement] api_tracer: support wildcard, improve serialization, add stop
   - Support wildcard patterns (e.g. paddle._C_ops.*) to batch hook APIs
   - Add recursion guard so only the outermost hooked call is traced
   - Add stop_api_tracer() to unload all hooks and restore original APIs
   ```

   确认后执行：

   ```bash
   git add <confirmed-files>
   git commit -m "<generated-message>"
   ```

4. **推送分支**：

   默认推送到 `dongbaiyue` 远程，创建与本地同名的远程分支。推送前向用户确认：

   > 即将执行：`git push -u dongbaiyue <branch-name>`，是否确认？

   确认后执行：

   ```bash
   git push -u dongbaiyue <branch-name>
   ```

   若需推送到其他 remote，可执行 `git remote -v` 查看可用列表后由用户指定。

5. **创建 PR**，使用 gh CLI：

   **确定目标分支**：通过当前分支的 merge-base 推断来源分支：

   ```bash
   git log --oneline --decorate | head -20
   ```

   **准备 PR body**：检查仓库根目录是否存在 PR 模板（注意大小写均需检查）：

   ```bash
   cat .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null || cat .github/pull_request_template.md 2>/dev/null
   ```

   若存在模板，按模板格式填写；若无，使用步骤3的 commit message bullet 列表作为 body。

   **创建前向用户确认**，展示以下信息并等待确认：

   > - 标题：`<title>`
   > - 目标分支：`<base-branch>`
   > - body 预览：`<pr-body>`
   > - 是否需要 Draft？（默认否）

   确认后执行：

   ```bash
   gh pr create \
     --base <base-branch> \
     --title "<title>" \
     --body "<pr-body>"
   ```

   PR 创建成功后，将输出的 URL 展示给用户。
