# 查询文档评论

查询文档的底部评论和侧边评论。

## API信息

- **接口**: `POST /ku/openapi/queryComments`
- **Python方法**: `client.query_comments(doc_id, query_bottom_comment, query_side_comment, page_num, page_size)`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| docId | string | 是 | - | 文档ID |
| queryBottomComment | boolean | 否 | true | 是否查询底部评论 |
| querySideComment | boolean | 否 | true | 是否查询侧边评论 |
| pageNum | int | 否 | 1 | 页码 |
| pageSize | int | 否 | 10 | 每页数量 |

## 响应示例

```json
{
  "returnCode": 200,
  "returnMessage": "SUCCESS",
  "result": {
    "bottomComments": [...],
    "sideComments": [...],
    "total": 25
  }
}
```

## Python调用示例

```python
from scripts import KuApiClient

client = KuApiClient()
result = client.query_comments(
    doc_id="WKoT7ltTnjU1oW",
    query_bottom_comment=True,
    query_side_comment=True,
    page_num=1,
    page_size=10
)
```
