---
name: ku-doc-manage
description: 百度知识库(ku.baidu-int.com)文档管理。触发词:知识库URL/文档/知识库/库/ku文档/创建文档/查询文档/复制文档/移动文档/文档权限/文档列表/文档评论/文档内容/浏览记录/流程图导出。
---

# 知识库文档管理 Skill

百度知识库文档操作技能集,基于知识库OpenAPI官方文档开发,使用签名认证方式。

## 术语说明

### 用户名 (username/creator_username)

在API中涉及的 `username`、`creator_username`、`operator_username` 等参数,**默认指当前用户的邮箱前缀或用户名**。

- 如果用户没有明确指定username值,应尝试从上下文中获取当前用户的邮箱前缀或用户名信息或者本地 git config user.name && git config user.email，取 email 前缀
- 邮箱前缀示例: `zhangsan@baidu.com` → 用户名为 `zhangsan`
- 适用于所有需要用户身份标识的API操作(创建文档、复制文档、修改权限等)

### 文档ID (doc_id) 和知识库ID (repo_id/repository_guid)

知识库URL中包含了文档ID和知识库ID信息,可以通过URL路径来识别:

**知识库URL格式**: `https://ku.baidu-int.com/knowledge/{path1}/{path2}/{path3}/{path4}`
  - **文档ID**: 最后一个斜杆后的字符串 (path4) → `AseK3nnVbJTu1J`
  - **知识库ID**: 倒数第二个斜杆后的字符串 (path3) → `E3d4LRExEl`

- **包含3个path值的URL** (知识库首页):
  - **知识库ID**: 最后一个斜杆后的字符串 (path3) → `E3d4LRExEl`

**提取示例**:

| URL类型 | 示例URL | 文档ID | 知识库ID |
|---------|---------|--------|----------|
| 文档页面 | `https://ku.baidu-int.com/knowledge/A/B/C/D` | `D` | `C` |
| 知识库首页 | `https://ku.baidu-int.com/knowledge/A/B/C/` | - | `C` |

**在API中的使用**:
- `doc_id` / `docId` / `doc_guid` - 都指文档ID
- `repo_id` / `repository_guid` - 都指知识库ID

## 功能概览

本技能集提供13个核心API,按功能分类:

### 📄 文档管理类 (5个)
- **query_content** - 查询文档正文内容
- **query_repo** - 分页查询知识库文档列表
- **create_doc** - 创建文档(支持3种模式)
- **copy_doc** - 复制文档
- **move_doc** - 移动文档

### 👥 权限管理类 (4个)
- **query_permission** - 查询用户对文档的权限
- **add_member** - 为文档添加成员
- **update_member** - 更新文档成员权限
- **change_scope** - 修改文档公开范围

### 💬 互动数据类 (2个)
- **query_comments** - 查询文档评论
- **query_recent_view** - 查询文档浏览记录

### 🎨 高级功能类 (2个)
- **query_flowchart** - 导出流程图数据
- **query_user_info** - 查询用户个人信息(含个人知识库ID)

## 快速开始

### 安装依赖

```bash
pip install requests
```

### 基本使用

```python
# 导入客户端
from scripts import KuApiClient

# 初始化客户端(自动认证)
client = KuApiClient()

# 查询文档内容
result = client.query_content(doc_id="WKoT7ltTnjU1oW")

# 查询知识库文档列表
result = client.query_repo(repo_id="E3d4LRExEl", page_num=1, page_size=10)

# 创建文档到个人知识库
result = client.create_doc(
    creator_username="zhangsan",
    title="我的笔记",
    content="笔记内容"
)
```

## API详细文档

每个API的详细文档(参数说明、调用示例、应用场景)已拆分到独立文件中。

**Agent使用说明**:
1. 根据用户需求判断需要哪个API
2. 读取 `references/` 目录下对应的markdown文档
3. 参考文档中的参数说明和示例代码完成任务

**文档索引**: 查看 [references/API_INDEX.md](./references/API_INDEX.md) 获取完整API列表和使用说明。

## 认证配置

### 两种认证方式

#### 1. 个人身份认证(默认,推荐)

- **TOKEN获取**: 访问 https://console.cloud.baidu-int.com/onetool/auth-manage/my-services
- **设置方式**:
  ```bash
  export COMATE_AUTH_TOKEN="your-token-here"
  ```
- TOKEN也可自动从 `~/.comate/login` 文件读取
- TOKEN有效期24小时,过期后需重新授权

#### 2. 数字员工身份认证(自动降级)

- 配置文件: `scripts/config.yaml`
- 当个人认证失败时自动切换
- 手动指定: `client = KuApiClient(use_digital_auth=True)`

### 认证流程说明

**自动切换触发条件**:
- TOKEN为空或读取失败 → 自动切换到数字员工身份认证(无需用户干预)

**Token过期时的用户引导**:
当检测到以下情况时,不会自动切换认证方式,而是引导用户重新授权:
- HTTP状态码为403
- 响应体中返回码为403或60413

系统将提示用户以下信息:
```
⚠️  Token认证失败(错误码:{error_code})
💡 Token有24小时有效期,请访问以下地址完成授权:
   https://console.cloud.baidu-int.com/onetool/auth-manage/my-services/auth-service
```

**认证流程总结**:
1. **TOKEN为空或读取失败** → 自动切换到数字员工认证(无需用户干预)
2. **TOKEN过期(403/60413)** → 提示用户重新授权(需要用户操作)
3. **数字员工认证失败** → 检查config.yaml中的AK/SK配置

### 配置文件位置

`scripts/config.yaml`:
```yaml
digital_auth:
  ak: "your_access_key"
  sk: "your_secret_key"
```

## 客户端方法速查

| 方法 | 说明 | 详细文档 |
|------|------|---------|
| `query_content(doc_id, url, show_doc_info)` | 查询文档内容 | [query_content.md](./references/query_content.md) |
| `query_repo(repo_id, page_num, page_size, ...)` | 查询文档列表 | [query_repo.md](./references/query_repo.md) |
| `create_doc(repository_guid, title, content, ...)` | 创建文档 | [create_doc.md](./references/create_doc.md) |
| `copy_doc(doc_id, operator_username, ...)` | 复制文档 | [copy_doc.md](./references/copy_doc.md) |
| `move_doc(doc_id, to_repo_guid, ...)` | 移动文档 | [move_doc.md](./references/move_doc.md) |
| `query_permission(doc_id, usernames)` | 查询权限 | [query_permission.md](./references/query_permission.md) |
| `add_member(doc_id, usernames, role_name)` | 添加成员 | [add_member.md](./references/add_member.md) |
| `update_member(doc_id, username, role_name)` | 更新成员 | [update_member.md](./references/update_member.md) |
| `change_scope(doc_id, scope, operator_username)` | 修改公开范围 | [change_scope.md](./references/change_scope.md) |
| `query_comments(doc_id, page_num, page_size, ...)` | 查询评论 | [query_comments.md](./references/query_comments.md) |
| `query_recent_view(doc_id, begin_time, end_time, ...)` | 查询浏览记录 | [query_recent_view.md](./references/query_recent_view.md) |
| `query_flowchart(doc_guid, flowchart_id)` | 导出流程图 | [query_flowchart.md](./references/query_flowchart.md) |
| `query_user_info(username)` | 查询用户信息 | [query_user_info.md](./references/query_user_info.md) |

## 常见错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未授权(Token无效或过期) |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 60413 | 无权限访问用户 |

## 权限角色说明

| 角色名称 | canRead | canUpdate | 说明 |
|----------|---------|-----------|------|
| DocReader | ✓ | ✗ | 只读成员,可查看文档 |
| DocMember | ✓ | ✓ | 可编辑成员,可查看、编辑文档 |
| DocAdmin | ✓ | ✓ | 页面管理员,可查看、编辑、管理文档和成员 |
