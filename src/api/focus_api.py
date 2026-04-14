"""
Focus API封装模块

本模块封装了Focus相关的API接口，提供统一的API调用接口。
主要功能：
- create_and_top_level接口：创建并获取focus
- top_level接口：获取focus列表
- hierarchy接口：获取指定focus的层级信息
- delete接口：删除指定focus

设计原则：
1. 单一职责：每个方法只负责一个API调用
2. 错误处理：使用@handle_api_errors装饰器统一处理异常
3. 日志记录：详细记录API调用过程
4. 响应验证：验证响应状态码，确保数据有效性

使用示例：
    from src.api.focus_api import FocusAPI

    # 创建并获取focus
    api = FocusAPI()
    response = api.create_and_top_level(
        endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus/create_and_top_level",
        data={"instruction": "今日安排"}
    )

    # 获取focus列表
    response = api.top_level(
        endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus/top-level"
    )

    # 获取指定focus的层级信息
    response = api.hierarchy(
        endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus",
        focus_id="50e0cb8d-dcb2-4017-af64-79f33e816fbf"
    )

    # 删除指定focus
    response = api.delete(
        endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus",
        focus_id="50e0cb8d-dcb2-4017-af64-79f33e816fbf"
    )
"""

from src.utils.http_client import build_api_client
from src.utils.error_handler import handle_api_errors
from src.utils.exceptions import InvalidResponseError
from src.utils.logger import get_logger
from typing import Optional, Dict, Any

logger = get_logger("focus_api")


class FocusAPI:
    """
    Focus API封装类

    封装了Focus相关的所有API接口，提供统一的调用方式。
    所有方法都使用@handle_api_errors装饰器进行异常处理。

    方法：
        create_and_top_level(endpoint, data, headers, check_status_code) - 创建并获取focus
        top_level(endpoint, headers, check_status_code) - 获取focus列表
        hierarchy(endpoint, focus_id, headers, check_status_code) - 获取指定focus的层级信息
        delete(endpoint, focus_id, headers, check_status_code) - 删除指定focus

    使用示例：
        api = FocusAPI()

        # 创建并获取focus
        response = api.create_and_top_level(
            endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus/create_and_top_level",
            data={"instruction": "今日安排"}
        )

        # 使用自定义headers
        custom_headers = {"Authorization": "token xxx"}
        response = api.create_and_top_level(
            endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus/create_and_top_level",
            data={"instruction": "今日安排"},
            headers=custom_headers
        )

        # 获取focus列表
        response = api.top_level(
            endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus/top-level"
        )

        # 获取指定focus的层级信息
        response = api.hierarchy(
            endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus",
            focus_id="50e0cb8d-dcb2-4017-af64-79f33e816fbf"
        )

        # 删除指定focus
        response = api.delete(
            endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus",
            focus_id="50e0cb8d-dcb2-4017-af64-79f33e816fbf"
        )
    """

    @staticmethod
    @handle_api_errors
    def create_and_top_level(
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None,
        check_status_code: bool = True,
        use_env_token: bool = True,
    ):
        """
        创建并获取focus

        根据指令创建focus并返回focus列表。

        Args:
            endpoint: API端点路径，如"/intent-os-mindspace-multi-agent-api/method/api/focus/create_and_top_level"
            data: 请求数据，包含instruction字段
            headers: 自定义请求头（可选）。如果提供，将使用自定义headers代替默认headers。
            check_status_code: 是否验证状态码，默认为True。如果设为False，则允许非200状态码。

        Returns:
            requests.Response: 响应对象，包含focus列表

        Raises:
            InvalidResponseError: 当响应状态码不是200时抛出（除非check_status_code=False）

        示例：
            response = api.create_and_top_level(
                endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus/create_and_top_level",
                data={"instruction": "今日安排"}
            )

            # 使用自定义headers
            custom_headers = {"Authorization": "token xxx"}
            response = api.create_and_top_level(
                endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus/create_and_top_level",
                data={"instruction": "今日安排"},
                headers=custom_headers
            )

        注意：
            - data必须是字典格式
            - instruction字段必填
            - 成功时返回200
            - 如果check_status_code=False，不验证状态码，直接返回响应
        """
        logger.info(f"调用create_and_top_level接口 - endpoint: {endpoint}")
        client = build_api_client(headers=headers, use_env_token=use_env_token)
        response = client.post(endpoint, json=data)

        if check_status_code and response.status_code != 200:
            logger.error(f"create_and_top_level接口返回异常状态码: {response.status_code}")
            raise InvalidResponseError(
                message=f"create_and_top_level接口返回异常状态码: {response.status_code}",
                response_data={"status_code": response.status_code, "body": response.text}
            )

        logger.info(f"create_and_top_level接口调用成功 - 状态码: {response.status_code}")
        return response

    @staticmethod
    @handle_api_errors
    def top_level(
        endpoint: str,
        headers: Optional[Dict[str, Any]] = None,
        check_status_code: bool = True,
        use_env_token: bool = True,
    ):
        """
        获取focus列表

        获取当前用户的focus列表。

        Args:
            endpoint: API端点路径，如"/intent-os-mindspace-multi-agent-api/method/api/focus/top-level"
            headers: 自定义请求头（可选）。如果提供，将使用自定义headers代替默认headers。
            check_status_code: 是否验证状态码，默认为True。如果设为False，则允许非200状态码。

        Returns:
            requests.Response: 响应对象，包含focus列表

        Raises:
            InvalidResponseError: 当响应状态码不是200时抛出（除非check_status_code=False）

        示例：
            response = api.top_level(
                endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus/top-level"
            )

            # 使用自定义headers
            custom_headers = {"Authorization": "token xxx"}
            response = api.top_level(
                endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus/top-level",
                headers=custom_headers
            )

        注意：
            - 这是一个GET请求，不需要请求体
            - 成功时返回200
            - 如果check_status_code=False，不验证状态码，直接返回响应
        """
        logger.info(f"调用top_level接口 - endpoint: {endpoint}")
        client = build_api_client(headers=headers, use_env_token=use_env_token)
        response = client.get(endpoint)

        if check_status_code and response.status_code != 200:
            logger.error(f"top_level接口返回异常状态码: {response.status_code}")
            raise InvalidResponseError(
                message=f"top_level接口返回异常状态码: {response.status_code}",
                response_data={"status_code": response.status_code, "body": response.text}
            )

        logger.info(f"top_level接口调用成功 - 状态码: {response.status_code}")
        return response

    @staticmethod
    @handle_api_errors
    def hierarchy(
        endpoint: str,
        focus_id: str,
        headers: Optional[Dict[str, Any]] = None,
        check_status_code: bool = True,
        use_env_token: bool = True,
    ):
        """
        获取指定focus的层级信息

        根据focusID获取该focus的详细层级信息。

        Args:
            endpoint: API端点路径（不包含focus_id），如"/intent-os-mindspace-multi-agent-api/method/api/focus"
            focus_id: focusID，如"50e0cb8d-dcb2-4017-af64-79f33e816fbf"
            headers: 自定义请求头（可选）。如果提供，将使用自定义headers代替默认headers。
            check_status_code: 是否验证状态码，默认为True。如果设为False，则允许非200状态码。

        Returns:
            requests.Response: 响应对象，包含focus层级信息

        Raises:
            InvalidResponseError: 当响应状态码不是200时抛出（除非check_status_code=False）

        示例：
            response = api.hierarchy(
                endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus",
                focus_id="50e0cb8d-dcb2-4017-af64-79f33e816fbf"
            )

            # 使用自定义headers
            custom_headers = {"Authorization": "token xxx"}
            response = api.hierarchy(
                endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus",
                focus_id="50e0cb8d-dcb2-4017-af64-79f33e816fbf",
                headers=custom_headers
            )

        注意：
            - 这是一个GET请求，不需要请求体
            - 最终请求路径为: {endpoint}/{focus_id}/hierarchy
            - 成功时返回200
            - 如果check_status_code=False，不验证状态码，直接返回响应
        """
        endpoint_with_id = f"{endpoint}/{focus_id}/hierarchy"
        logger.info(f"调用hierarchy接口 - endpoint: {endpoint_with_id}")
        client = build_api_client(headers=headers, use_env_token=use_env_token)
        response = client.get(endpoint_with_id)

        if check_status_code and response.status_code != 200:
            logger.error(f"hierarchy接口返回异常状态码: {response.status_code}")
            raise InvalidResponseError(
                message=f"hierarchy接口返回异常状态码: {response.status_code}",
                response_data={"status_code": response.status_code, "body": response.text}
            )

        logger.info(f"hierarchy接口调用成功 - 状态码: {response.status_code}")
        return response

    @staticmethod
    @handle_api_errors
    def delete(
        endpoint: str,
        focus_id: str,
        headers: Optional[Dict[str, Any]] = None,
        check_status_code: bool = True,
        use_env_token: bool = True,
    ):
        """
        删除指定focus

        根据focusID删除指定的focus。

        Args:
            endpoint: API端点路径（不包含focus_id），如"/intent-os-mindspace-multi-agent-api/method/api/focus"
            focus_id: focusID，如"b897e118-1d9d-4476-afe2-cc1f7f1e9900"
            headers: 自定义请求头（可选）。如果提供，将使用自定义headers代替默认headers。
            check_status_code: 是否验证状态码，默认为True。如果设为False，则允许非200状态码。

        Returns:
            requests.Response: 响应对象

        Raises:
            InvalidResponseError: 当响应状态码不是200时抛出（除非check_status_code=False）

        示例：
            response = api.delete(
                endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus",
                focus_id="b897e118-1d9d-4476-afe2-cc1f7f1e9900"
            )

            # 使用自定义headers
            custom_headers = {"Authorization": "token xxx"}
            response = api.delete(
                endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus",
                focus_id="b897e118-1d9d-4476-afe2-cc1f7f1e9900",
                headers=custom_headers
            )

        注意：
            - 这是一个DELETE请求，不需要请求体
            - 最终请求路径为: {endpoint}/{focus_id}
            - 成功时返回200或204
            - 如果check_status_code=False，不验证状态码，直接返回响应
        """
        endpoint_with_id = f"{endpoint}/{focus_id}"
        logger.info(f"调用delete接口 - endpoint: {endpoint_with_id}")
        client = build_api_client(headers=headers, use_env_token=use_env_token)
        response = client.delete(endpoint_with_id)

        if check_status_code and response.status_code not in [200, 204]:
            logger.error(f"delete接口返回异常状态码: {response.status_code}")
            raise InvalidResponseError(
                message=f"delete接口返回异常状态码: {response.status_code}",
                response_data={"status_code": response.status_code, "body": response.text}
            )

        logger.info(f"delete接口调用成功 - 状态码: {response.status_code}")
        return response
