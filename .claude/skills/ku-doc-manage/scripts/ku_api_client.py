#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库开放API Python客户端
基于SKILL.md文档开发
支持：查询文档内容、查询文档列表、创建文档、查询权限等
"""

import os
import sys
import json
import yaml
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any


class KuApiClient:
    """知识库开放API客户端"""

    # 定义两种认证方式的URL
    BASE_URL_PERSONAL = 'http://10.11.152.208:8701/api/process/ku'
    BASE_URL_DIGITAL = 'https://ku.baidu-int.com/wiki/so'

    @staticmethod
    def _load_config() -> Dict[str, str]:
        """
        从config.yaml文件读取数字员工认证配置

        Returns:
            dict: 包含ak和sk的字典，如果读取失败返回空字典
        """
        try:
            # 获取config.yaml文件路径（在scripts目录）
            current_dir = Path(__file__).parent
            config_path = current_dir / 'config.yaml'

            if not config_path.exists():
                return {}

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if config and 'digital_auth' in config:
                digital_auth = config['digital_auth']
                return {
                    'ak': digital_auth.get('ak', ''),
                    'sk': digital_auth.get('sk', '')
                }
        except Exception as e:
            print(f"⚠️  从config.yaml读取配置失败: {e}")

        return {}

    def __init__(self, base_url: str = None, ak: str = None, sk: str = None, token: str = None,
                 use_digital_auth: bool = False):
        """
        初始化API客户端

        Args:
            base_url: API基础URL，如果不指定则根据use_digital_auth自动选择
            ak: Access Key，用于数字员工身份认证(use_digital_auth=True时必须提供)
            sk: Secret Key，用于数字员工身份认证(use_digital_auth=True时必须提供)
            token: Bearer Token，用于个人身份认证，默认从环境变量或登录文件读取
            use_digital_auth: 是否直接使用数字员工身份认证，默认False（优先使用个人身份认证）
        """
        self.use_digital_auth = use_digital_auth

        # 从config.yaml读取数字员工配置（用于自动降级）
        self.config = self._load_config()

        # 数字员工身份认证: 直接使用传入的ak/sk，不依赖环境变量
        if use_digital_auth:
            # 优先使用传入的ak/sk，如果没有则尝试从配置文件读取
            self.ak = ak or self.config.get('ak', '')
            self.sk = sk or self.config.get('sk', '')

            if not self.ak or not self.sk:
                raise ValueError("使用数字员工身份认证时，必须提供有效的ak和sk参数，或在scripts/config.yaml中配置")
        else:
            # 个人身份认证模式，先不设置ak/sk（等需要时从配置读取）
            self.ak = None
            self.sk = None

        self.token = token or self._get_token()

        # 根据认证方式选择URL
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = self.BASE_URL_DIGITAL if use_digital_auth else self.BASE_URL_PERSONAL

        self.has_switched_to_digital = False  # 标记是否已经切换到数字员工认证
        
    def _get_token(self) -> str:
        """
        获取认证Token
        优先级：环境变量 > 登录文件

        Returns:
            str: Bearer Token，如果获取不到返回空字符串（支持数字员工认证）
        """
        # 方式1：从环境变量获取
        token = os.getenv('COMATE_AUTH_TOKEN')
        if token:
            return token.strip()

        # 方式2：从登录文件获取
        login_file = Path.home() / '.comate' / 'login'
        if login_file.exists():
            with open(login_file, 'r', encoding='utf-8') as f:
                token = f.read().strip()
                # 确保token不为空
                if token:
                    return token

        # 如果都获取不到，返回空字符串（将尝试使用数字员工认证）
        print("⚠️  未找到个人身份认证TOKEN，将尝试使用数字员工身份认证")
        print("💡  提示：如需使用个人身份认证，请按以下步骤操作：")
        print("   Token有24小时有效期,请访问以下地址完成授权:")
        print("   https://console.cloud.baidu-int.com/onetool/auth-manage/my-services/auth-service")
        print("\n" + "="*70)
        print("   或者访问以下地址重新初始化个人Token: https://console.cloud.baidu-int.com/onetool/auth-manage/my-services")
        print("   1. 复制您的个人Token")
        print("   2. 在openclaw中设置环境变量：COMATE_AUTH_TOKEN=\"your-token-here\"")
        return ""
    
    def _get_headers(self) -> Dict[str, str]:
        """
        构建请求头

        Returns:
            dict: HTTP请求头
        """
        headers = {
            'Content-Type': 'application/json',
            'x-ac-Authorization': self.token
        }

        # 只有使用数字员工认证时才添加 ak/sk
        if self.use_digital_auth:
            headers['ak'] = self.ak
            headers['sk'] = self.sk

        return headers
    
    def _switch_to_digital_auth(self):
        """切换到数字员工身份认证"""
        if not self.has_switched_to_digital:
            print("\n" + "="*70)
            print("🔄 个人身份认证失败，尝试切换到数字员工身份认证...")
            print("="*70)
            print("\n💡 如需使用个人身份认证，请按以下步骤操作：")
            print("   Token有24小时有效期,请访问以下地址完成授权:")
            print("   https://console.cloud.baidu-int.com/onetool/auth-manage/my-services/auth-service")
            print("\n" + "="*70)
            print("   或者访问以下地址重新初始化个人Token: https://console.cloud.baidu-int.com/onetool/auth-manage/my-services")
            print("   1. 复制您的个人Token")
            print("   2. 在openclaw中设置环境变量：COMATE_AUTH_TOKEN=\"your-token-here\"")

            # 从配置文件读取AK/SK
            if not self.ak or not self.sk:
                self.ak = self.config.get('ak', '')
                self.sk = self.config.get('sk', '')

            if not self.ak or not self.sk:
                print("="*70)
                print("❌ 切换到数字员工身份认证失败：未找到有效的AK/SK配置")
                print("="*70)
                print("\n请在 scripts/config.yaml 中配置 digital_auth.ak 和 digital_auth.sk")
                raise ValueError("切换到数字员工身份认证失败：未找到有效的AK/SK配置。请在scripts/config.yaml中配置digital_auth.ak和digital_auth.sk")

            self.base_url = self.BASE_URL_DIGITAL
            self.use_digital_auth = True
            self.has_switched_to_digital = True
            print(f"✅ 已切换到数字员工身份认证 (AK: {self.ak[:10]}...)\n")
            print("="*70 + "\n")
    
    def _request(self, endpoint: str, data: Dict[str, Any], retry_on_403: bool = True) -> Dict[str, Any]:
        """
        发送HTTP请求，支持自动切换认证方式

        Args:
            endpoint: API端点路径
            data: 请求数据
            retry_on_403: 是否在403错误时自动切换到数字员工认证重试

        Returns:
            dict: API响应结果
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)

            # 先尝试解析JSON响应
            try:
                result = response.json()
            except:
                # 如果无法解析JSON，按HTTP状态码处理
                if response.status_code == 403 and retry_on_403 and not self.has_switched_to_digital:
                    print(f"\n⚠️  个人身份认证失败 (HTTP 403)")
                    self._switch_to_digital_auth()
                    return self._request(endpoint, data, retry_on_403=False)
                response.raise_for_status()
                raise

            # 检查响应体中的code字段（某些API返回500状态码但响应体中包含真实错误码）
            response_code = result.get('code') or result.get('returnCode')

            if response_code in [403, 60413] and retry_on_403 and not self.has_switched_to_digital:
                error_msg = result.get('msg') or result.get('returnMessage', '')
                print(f"\n⚠️  个人身份认证失败 (code: {response_code}, {error_msg})")
                self._switch_to_digital_auth()
                # 重试请求
                return self._request(endpoint, data, retry_on_403=False)

            # 检查HTTP状态码
            if response.status_code == 403 and retry_on_403 and not self.has_switched_to_digital:
                print(f"\n⚠️  个人身份认证失败 (HTTP 403)")
                self._switch_to_digital_auth()
                return self._request(endpoint, data, retry_on_403=False)

            # 如果状态码不是2xx，抛出异常
            response.raise_for_status()

            return result

        except requests.exceptions.RequestException as e:
            # 如果是个人身份认证失败且TOKEN为空或无效，尝试数字员工认证
            if not self.token and not self.has_switched_to_digital and retry_on_403:
                print(f"\n⚠️  个人身份认证TOKEN为空或无效")
                self._switch_to_digital_auth()
                return self._request(endpoint, data, retry_on_403=False)

            print(f"❌ 请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            raise
    
    def query_content(self, doc_id: str = None, url: str = None, show_doc_info: bool = True) -> Dict[str, Any]:
        """
        查询文档正文内容
        
        Args:
            doc_id: 文档ID
            url: 文档URL
            show_doc_info: 是否显示文档信息
            
        Returns:
            dict: 文档内容数据
        """
        if not doc_id and not url:
            raise ValueError("docId和url至少提供一个")
        
        data = {
            "showDocInfo": show_doc_info
        }
        if doc_id:
            data["docId"] = doc_id
        if url:
            data["url"] = url
            
        return self._request("/ku/openapi/queryContent", data)
    
    def query_repo(self, 
                   repo_id: str,
                   page_num: int = 1,
                   page_size: int = 10,
                   order_direction: str = "desc",
                   parent_doc_guid: str = None,
                   doc_guids: List[str] = None,
                   urls: List[str] = None,
                   show_doc_creator_info: bool = True,
                   show_doc_publisher_info: bool = True,
                   order_by: str = "publishTime") -> Dict[str, Any]:
        """
        分页查询知识库文档列表
        
        Args:
            repo_id: 知识库ID
            page_num: 页码
            page_size: 每页数量
            order_direction: 排序方向（desc/asc）
            parent_doc_guid: 父文档ID
            doc_guids: 文档ID列表
            urls: URL列表
            show_doc_creator_info: 是否显示创建者信息
            show_doc_publisher_info: 是否显示发布者信息
            order_by: 排序字段
            
        Returns:
            dict: 文档列表数据
        """
        data = {
            "repoId": repo_id,
            "pageNum": page_num,
            "pageSize": page_size,
            "orderDirection": order_direction
        }
        
        if parent_doc_guid is not None:
            data["parentDocGuid"] = parent_doc_guid
        if doc_guids:
            data["docGuids"] = doc_guids
        if urls:
            data["urls"] = urls
        if show_doc_creator_info:
            data["showDocCreatorInfo"] = show_doc_creator_info
        if show_doc_publisher_info:
            data["showDocPublisherInfo"] = show_doc_publisher_info
        if order_by:
            data["orderBy"] = order_by
            
        return self._request("/ku/openapi/queryRepo", data)
    
    def query_permission(self, doc_id: str, usernames: List[str]) -> Dict[str, Any]:
        """
        查询用户对文档的权限
        
        Args:
            doc_id: 文档ID
            usernames: 用户名列表
            
        Returns:
            dict: 权限信息
        """
        data = {
            "docId": doc_id,
            "usernames": usernames
        }
        return self._request("/ku/openapi/queryPermission", data)
    
    def create_doc(self,
                   repository_guid: str,
                   creator_username: str = None,
                   title: str = None,
                   content: str = "",
                   parent_doc_guid: str = None,
                   create_mode: int = 2,
                   template_doc_guid: str = None) -> Dict[str, Any]:
        """
        创建文档

        Args:
            repository_guid: 知识库ID
            creator_username: 创建者用户名
            title: 文档标题
            content: 文档内容
            parent_doc_guid: 父文档ID
            create_mode: 文档创建模式,1-创建空文档,2-指定文档内容创建,3-指定源文档复制创建,默认为2
            template_doc_guid: 待复制的目标文档ID,当且仅当create_mode=3时必须有值

        Returns:
            dict: 创建结果
        """
        data = {
            "repositoryGuid": repository_guid,
            "content": content,
            "createMode": create_mode
        }

        if creator_username:
            data["creatorUsername"] = creator_username
        if title:
            data["title"] = title
        if parent_doc_guid:
            data["parentDocGuid"] = parent_doc_guid
        if template_doc_guid:
            data["templateDocGuid"] = template_doc_guid

        return self._request("/ku/openapi/createDoc", data)

    def add_member(self, doc_id: str, usernames: List[str], role_name: str = "DocReader") -> Dict[str, Any]:
        """
        添加文档成员

        Args:
            doc_id: 文档ID
            usernames: 用户名列表（邮箱前缀）
            role_name: 角色名称，默认DocReader。可选值：
                - DocReader: 可读
                - DocMember: 可编辑
                - DocAdmin: 管理员

        Returns:
            dict: 操作结果
        """
        data = {
            "docId": doc_id,
            "usernames": usernames,
            "roleName": role_name
        }
        return self._request("/ku/openapi/addMember", data)

    def update_member(self, doc_id: str, username: str, role_name: str) -> Dict[str, Any]:
        """
        更新文档成员权限

        Args:
            doc_id: 文档ID
            username: 待更新的用户名（邮箱前缀）
            role_name: 新的角色名称：DocReader、DocMember、DocAdmin

        Returns:
            dict: 操作结果
        """
        data = {
            "docId": doc_id,
            "username": username,
            "roleName": role_name
        }
        return self._request("/ku/openapi/updateMember", data)

    def copy_doc(self,
                 doc_id: str,
                 operator_username: str = None,
                 to_repo_guid: str = None,
                 to_parent_guid: str = None,
                 new_title: str = None) -> Dict[str, Any]:
        """
        复制文档

        Args:
            doc_id: 待复制的源文档ID
            operator_username: 操作者用户名
            to_repo_guid: 目标知识库ID，不传则默认为源文档所在库
            to_parent_guid: 目标父目录ID，不传则默认为源文档同级
            new_title: 新文档标题，不传则默认为"源标题的复制"

        Returns:
            dict: 新文档信息，包含docGuid、url、title
        """
        data = {
            "docId": doc_id
        }
        if operator_username:
            data["operatorUsername"] = operator_username
        if to_repo_guid:
            data["toRepoGuid"] = to_repo_guid
        if to_parent_guid:
            data["toParentGuid"] = to_parent_guid
        if new_title:
            data["newTitle"] = new_title
        return self._request("/ku/openapi/copyDoc", data)

    def move_doc(self,
                 doc_id: str,
                 to_repo_guid: str,
                 operator_username: str = None,
                 to_parent_guid: str = None,
                 to_adjacent_doc_guid: str = None,
                 upper: bool = False) -> Dict[str, Any]:
        """
        移动文档

        Args:
            doc_id: 待移动的源文档ID
            to_repo_guid: 目标知识库ID
            operator_username: 操作者用户名
            to_parent_guid: 目标父目录ID，不传则默认为根目录
            to_adjacent_doc_guid: 目标相邻文档ID
            upper: 是否移动到目标上方，默认False

        Returns:
            dict: 移动后的文档信息，包含docGuid、url
        """
        data = {
            "docId": doc_id,
            "toRepoGuid": to_repo_guid
        }
        if operator_username:
            data["operatorUsername"] = operator_username
        if to_parent_guid:
            data["toParentGuid"] = to_parent_guid
        if to_adjacent_doc_guid:
            data["toAdjacentDocGuid"] = to_adjacent_doc_guid
        if upper:
            data["upper"] = upper
        return self._request("/ku/openapi/moveDoc", data)

    def change_scope(self, doc_id: str, scope: int, operator_username: str = None) -> Dict[str, Any]:
        """
        修改文档公开范围

        Args:
            doc_id: 文档ID
            scope: 权限范围：5-公开可读，6-公开可编辑，20-私密
            operator_username: 操作者用户名，不传则使用ak对应的用户名

        Returns:
            dict: 操作结果
        """
        data = {
            "docId": doc_id,
            "scope": scope
        }
        if operator_username:
            data["operatorUsername"] = operator_username
        return self._request("/ku/openapi/changeScope", data)

    def query_comments(self,
                      doc_id: str,
                      query_bottom_comment: bool = True,
                      query_side_comment: bool = True,
                      page_num: int = 1,
                      page_size: int = 10) -> Dict[str, Any]:
        """
        查询文档评论

        Args:
            doc_id: 文档ID
            query_bottom_comment: 是否查询底部评论，默认True
            query_side_comment: 是否查询侧边评论，默认True
            page_num: 页码，默认1
            page_size: 每页数量，默认10

        Returns:
            dict: 评论数据，包含bottomComments、sideComments、total
        """
        data = {
            "docId": doc_id,
            "queryBottomComment": query_bottom_comment,
            "querySideComment": query_side_comment,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self._request("/ku/openapi/queryComments", data)

    def query_recent_view(self,
                         doc_id: str,
                         begin_time: int = None,
                         end_time: int = None,
                         page_num: int = 1,
                         page_size: int = 10) -> Dict[str, Any]:
        """
        查询文档最近浏览信息

        Args:
            doc_id: 文档ID
            begin_time: 记录起始时间（毫秒级时间戳），不传则默认为当天起始时间
            end_time: 记录结束时间（毫秒级时间戳），不传则默认为当前时间
            page_num: 页码，默认1
            page_size: 每页数量，默认10

        Returns:
            dict: 浏览信息，包含repositoryGuid、docGuid、totalViewers、count、data
        """
        data = {
            "docId": doc_id,
            "pageNum": page_num,
            "pageSize": page_size
        }
        if begin_time is not None:
            data["beginTime"] = begin_time
        if end_time is not None:
            data["endTime"] = end_time
        return self._request("/ku/openapi/queryRecentView", data)

    def query_flowchart(self, doc_guid: str, flowchart_id: str) -> Dict[str, Any]:
        """
        导出流程图数据

        Args:
            doc_guid: 文档ID
            flowchart_id: 流程图ID

        Returns:
            dict: 流程图数据，包含docGuid、flowchartId、content（mxGraph格式的XML）
        """
        data = {
            "docGuid": doc_guid,
            "flowchartId": flowchart_id
        }
        return self._request("/ku/openapi/queryFlowchart", data)

    def query_user_info(self, username: str) -> Dict[str, Any]:
        """
        查询用户个人信息

        查询指定用户的个人信息，包括个人知识库ID等。当需要创建文档但不知道目标知识库ID时，
        可以使用此API获取用户的个人知识库ID。

        Args:
            username: 用户名（邮箱前缀）

        Returns:
            dict: 用户信息数据，包含个人知识库ID

        Example:
            >>> client = KuApiClient()
            >>> result = client.query_user_info(username="zhangsan")
            >>> if result.get('returnCode') == 200:
            >>>     user_info = result['result']['userPersonalRepo']
            >>>     personal_repo_id = user_info['repositoryGuid']
            >>>     print(f"个人知识库ID: {personal_repo_id}")
        """
        data = {
            "username": username
        }
        return self._request("/ku/openapi/queryUserInfo", data)


def main():
    """示例用法"""
    # 初始化客户端
    client = KuApiClient()

    print("=" * 60)
    print("知识库开放API Python客户端示例 - 完整14个API")
    print("=" * 60)

    # 示例1: 查询文档内容
    print("\n1. 查询文档内容")
    print("-" * 60)
    try:
        result = client.query_content(doc_id="WKoT7ltTnjU1oW")
        if result.get('returnCode') == 200:
            doc_info = result['result'].get('docInfo', {})
            print(f"✅ 文档标题: {doc_info.get('name')}")
            print(f"✅ 创建者: {doc_info.get('creatorUserInfo', {}).get('nickname')}")
            print(f"✅ 文档URL: {doc_info.get('url')}")
        else:
            print(f"❌ 查询失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例2: 查询知识库文档列表
    print("\n2. 查询知识库文档列表")
    print("-" * 60)
    try:
        result = client.query_repo(
            repo_id="E3d4LRExEl",
            page_num=1,
            page_size=5
        )
        if result.get('returnCode') == 200:
            docs = result['result'].get('data', [])
            total = result['result'].get('total', 0)
            print(f"✅ 共找到 {total} 篇文档，显示前5篇:")
            for i, doc in enumerate(docs, 1):
                print(f"  {i}. {doc.get('name')} (ID: {doc.get('docGuid')})")
        else:
            print(f"❌ 查询失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例3: 创建文档
    print("\n3. 创建文档")
    print("-" * 60)
    try:
        result = client.create_doc(
            repository_guid="E3d4LRExEl",
            creator_username="zhangsan",
            title="API测试文档",
            content="这是一篇通过API创建的测试文档"
        )
        if result.get('returnCode') == 200:
            doc_info = result['result']
            print(f"✅ 文档创建成功")
            print(f"  - 文档ID: {doc_info.get('docGuid')}")
            print(f"  - 文档URL: {doc_info.get('url')}")
        else:
            print(f"❌ 创建失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例4: 查询用户权限
    print("\n4. 查询用户权限")
    print("-" * 60)
    try:
        result = client.query_permission(
            doc_id="WKoT7ltTnjU1oW",
            usernames=["zhangsan"]
        )
        if result.get('returnCode') == 200:
            permissions = result.get('result', [])
            for perm in permissions:
                print(f"✅ 用户: {perm.get('username')}")
                print(f"  - 可读: {perm.get('canRead')}")
                print(f"  - 可写: {perm.get('canUpdate')}")
                print(f"  - 角色: {perm.get('roleName')}")
        else:
            print(f"❌ 查询失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例5: 添加文档成员
    print("\n5. 添加文档成员")
    print("-" * 60)
    try:
        result = client.add_member(
            doc_id="WKoT7ltTnjU1oW",
            usernames=["zhangsan"],
            role_name="DocReader"
        )
        if result.get('returnCode') == 200:
            print(f"✅ 成员添加成功")
        else:
            print(f"❌ 添加失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例6: 更新文档成员权限
    print("\n6. 更新文档成员权限")
    print("-" * 60)
    try:
        result = client.update_member(
            doc_id="WKoT7ltTnjU1oW",
            username="zhangsan",
            role_name="DocMember"
        )
        if result.get('returnCode') == 200:
            print(f"✅ 权限更新成功")
        else:
            print(f"❌ 更新失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例7: 查询文档评论
    print("\n7. 查询文档评论")
    print("-" * 60)
    try:
        result = client.query_comments(
            doc_id="WKoT7ltTnjU1oW",
            page_num=1,
            page_size=5
        )
        if result.get('returnCode') == 200:
            total = result['result'].get('total', 0)
            print(f"✅ 共有 {total} 条评论")
        else:
            print(f"❌ 查询失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例8: 查询文档浏览记录
    print("\n8. 查询文档最近浏览信息")
    print("-" * 60)
    try:
        result = client.query_recent_view(
            doc_id="WKoT7ltTnjU1oW",
            page_num=1,
            page_size=5
        )
        if result.get('returnCode') == 200:
            view_info = result['result']
            print(f"✅ 总浏览人数: {view_info.get('totalViewers')}")
            print(f"✅ 浏览记录数: {view_info.get('count')}")
        else:
            print(f"❌ 查询失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例9: 复制文档
    print("\n9. 复制文档")
    print("-" * 60)
    try:
        result = client.copy_doc(
            doc_id="WKoT7ltTnjU1oW",
            operator_username="zhangsan",
            new_title="文档副本"
        )
        if result.get('returnCode') == 200:
            doc_info = result['result']
            print(f"✅ 文档复制成功")
            print(f"  - 新文档ID: {doc_info.get('docGuid')}")
        else:
            print(f"❌ 复制失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例10: 修改文档公开范围
    print("\n10. 修改文档公开范围")
    print("-" * 60)
    try:
        result = client.change_scope(
            doc_id="WKoT7ltTnjU1oW",
            scope=5,  # 5-公开可读
            operator_username="zhangsan"
        )
        if result.get('returnCode') == 200:
            print(f"✅ 公开范围修改成功")
        else:
            print(f"❌ 修改失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例11: 导出流程图数据
    print("\n11. 导出流程图数据")
    print("-" * 60)
    try:
        result = client.query_flowchart(
            doc_guid="WKoT7ltTnjU1oW",
            flowchart_id="flowchart_123"
        )
        if result.get('returnCode') == 200:
            print(f"✅ 流程图数据导出成功")
        else:
            print(f"❌ 导出失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 示例12: 查询用户个人信息（获取个人知识库ID）
    print("\n12. 查询用户个人信息")
    print("-" * 60)
    try:
        result = client.query_user_info(username="zhangsan")
        if result.get('returnCode') == 200:
            user_info = result['result']['userPersonalRepo']
            personal_repo_id = user_info['repositoryGuid']
            print(f"✅ 用户个人信息查询成功")
            print(f"  - 用户名: {result['result'].get('username')}")
            print(f"  - 昵称: {result['result'].get('nickname')}")
            print(f"  - 个人知识库ID: {personal_repo_id}")
            print(f"  - 个人知识库名: {user_info.get('name')}")
        else:
            print(f"❌ 查询失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "=" * 60)
    print("示例执行完成 - 展示了12个常用API")
    print("=" * 60)


if __name__ == '__main__':
    main()