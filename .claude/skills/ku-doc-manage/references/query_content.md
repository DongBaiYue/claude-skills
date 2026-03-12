# 查询文档正文内容

根据文档ID或URL查询知识库文档的完整正文内容。

## API信息

- **接口**: `POST /ku/openapi/queryContent`
- **Python方法**: `client.query_content(doc_id, url, show_doc_info)`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| docId | string | 否* | 文档ID,知识库文档链接中以/分割后的最后一个字符串 |
| url | string | 否* | 文档完整URL链接 |
| show_doc_info | boolean | 否 | 是否返回文档元信息(标题、创建时间等) |

*注：docId和url至少提供一个

## 响应示例

```json
{
  "returnCode": 200,
  "returnMessage": "SUCCESS",
  "result": {
    "docId": "1xosIYvQX3qxeI",
    "title": "文档标题",
    "content": {...}
  }
}
```

## Python调用示例

```python
from scripts import KuApiClient

client = KuApiClient()

# 方式1: 使用文档ID
result = client.query_content(doc_id="WKoT7ltTnjU1oW")

# 方式2: 使用完整URL
result = client.query_content(url="https://ku.baidu-int.com/knowledge/xxx/xxx/xxx/WKoT7ltTnjU1oW")

# 方式3: 同时获取文档元信息
result = client.query_content(doc_id="WKoT7ltTnjU1oW", show_doc_info=True)
```

## 使用场景

- 获取文档的完整正文内容用于分析或处理
- 根据用户提供的URL快速查询文档内容
- 批量获取多个文档的内容
