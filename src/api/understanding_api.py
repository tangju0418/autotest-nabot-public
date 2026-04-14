"""
Understanding API封装模块

本模块封装了Understanding相关的API接口，提供统一的API调用接口。
主要功能：
- write接口：写入记忆数据
- read接口：读取记忆数据

设计原则：
1. 单一职责：每个方法只负责一个API调用
2. 错误处理：使用@handle_api_errors装饰器统一处理异常
3. 日志记录：详细记录API调用过程
4. 响应验证：验证响应状态码，确保数据有效性

使用示例：
    from src.api.understanding_api import UnderstandingAPI

    # 写入记忆数据
    api = UnderstandingAPI()
    response = api.write(
        endpoint="/invoke/planning-api/method/understanding/write",
        data=[{"scenario_id": "123", "scenario_type": "memory_custom"}]
    )

    # 读取记忆数据
    response = api.read(
        endpoint="/invoke/planning-api/method/understanding/read",
        user_id="user123",
        data=["我喜欢吃肉"]
    )

    # 使用自定义headers
    custom_headers = {"Authorization": "token xxx"}
    response = api.write(
        endpoint="/invoke/planning-api/method/understanding/write",
        data=[{"scenario_id": "123", "scenario_type": "memory_custom"}],
        headers=custom_headers
    )

    # 允许非200状态码（如400错误）
    response = api.write(
        endpoint="/invoke/planning-api/method/understanding/write",
        data=[{"scenario_id": "123", "scenario_type": "memory_custom"}],
        check_status_code=False
    )
"""

from src.utils.http_client import build_api_client
from src.utils.error_handler import handle_api_errors
from src.utils.exceptions import InvalidResponseError
from src.utils.logger import get_logger
from typing import Optional, Dict, Any, List

logger = get_logger("understanding_api")


class UnderstandingAPI:
    """
    Understanding API封装类

    封装了Understanding相关的所有API接口，提供统一的调用方式。
    所有方法都使用@handle_api_errors装饰器进行异常处理。

    方法：
        write(endpoint, data, headers, check_status_code) - 写入记忆数据
        read(endpoint, user_id, data, retrieval_options, headers, check_status_code) - 读取记忆数据

    使用示例：
        api = UnderstandingAPI()

        # 写入数据
        response = api.write(
            endpoint="/invoke/planning-api/method/understanding/write",
            data=[{"scenario_id": "123", "scenario_type": "memory_custom"}]
        )

        # 读取数据
        response = api.read(
            endpoint="/invoke/planning-api/method/understanding/read",
            user_id="user123",
            data=["我喜欢吃肉"]
        )

        # 使用自定义headers
        custom_headers = {"Authorization": "token xxx"}
        response = api.write(
            endpoint="/invoke/planning-api/method/understanding/write",
            data=[{"scenario_id": "123", "scenario_type": "memory_custom"}],
            headers=custom_headers
        )

        # 允许400状态码
        response = api.write(
            endpoint="/invoke/planning-api/method/understanding/write",
            data=[{"scenario_id": "123", "scenario_type": "memory_custom"}],
            check_status_code=False
        )
    """

    HTTP_METHOD_READ = "POST"
    HTTP_METHOD_WRITE = "POST"

    @staticmethod
    @handle_api_errors
    def write(
        endpoint: str,
        data: List[Dict[str, Any]],
        headers: Optional[Dict[str, Any]] = None,
        check_status_code: bool = True,
        use_env_token: bool = True,
    ):
        """
        写入记忆数据

        将用户的记忆数据写入系统，支持多种场景类型。

        Args:
            endpoint: API端点路径，如"/invoke/planning-api/method/understanding/write"
            data: 记忆数据列表，包含scenario_id、scenario_type、user_action等字段
            headers: 自定义请求头（可选）。如果提供，将使用自定义headers代替默认headers。
            check_status_code: 是否验证状态码，默认为True。如果设为False，则允许非200状态码（如400错误）。

        Returns:
            requests.Response: 响应对象，包含写入结果

        Raises:
            InvalidResponseError: 当响应状态码不是200或400时抛出（除非check_status_code=False）

        示例：
            response = api.write(
                endpoint="/invoke/planning-api/method/understanding/write",
                data=[{
                    "scenario_id": "memory_custom_123",
                    "scenario_type": "memory_custom",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "user_action": {
                        "type": "memory_custom",
                        "description": "我喜欢吃肉"
                    }
                }]
            )

            # 使用自定义headers
            custom_headers = {"Authorization": "token xxx"}
            response = api.write(
                endpoint="/invoke/planning-api/method/understanding/write",
                data=[{"scenario_id": "123", "scenario_type": "memory_custom"}],
                headers=custom_headers
            )

        注意：
            - data必须是列表格式
            - 每个元素必须包含scenario_id、scenario_type等必要字段
            - 成功时返回200，参数错误时返回400
            - 如果check_status_code=False，不验证状态码，直接返回响应
        """
        payload = {"data": data}
        logger.info(f"调用write接口 - endpoint: {endpoint}")
        client = build_api_client(headers=headers, use_env_token=use_env_token)
        response = client.post(endpoint, json=payload)

        if check_status_code and response.status_code not in [200, 400]:
            logger.error(f"write接口返回异常状态码: {response.status_code}")
            raise InvalidResponseError(
                message=f"write接口返回异常状态码: {response.status_code}",
                response_data={"status_code": response.status_code, "body": response.text}
            )

        logger.info(f"write接口调用成功 - 状态码: {response.status_code}")
        return response

    @staticmethod
    @handle_api_errors
    def read(
        endpoint: str,
        user_id: str,
        data: List[str],
        retrieval_options: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        check_status_code: bool = True,
        timeout: Optional[float] = None,
        use_env_token: bool = True,
    ):
        """
        读取记忆数据

        根据用户ID和查询数据读取系统中的记忆信息。

        Args:
            endpoint: API端点路径，如"/invoke/planning-api/method/understanding/read"
            user_id: 用户ID，用于标识用户身份
            data: 查询数据列表，如["我喜欢吃肉"]
            retrieval_options: 检索选项（可选），用于控制检索行为
            headers: 自定义请求头（可选）。如果提供，将使用自定义headers代替默认headers。
            check_status_code: 是否验证状态码，默认为True。如果设为False，则允许非200状态码（如400错误）。
            timeout: 本次请求超时秒数，默认None表示使用 HTTP 全局配置。

        Returns:
            requests.Response: 响应对象，包含查询到的记忆数据

        Raises:
            InvalidResponseError: 当响应状态码不是200或400时抛出（除非check_status_code=False）

        示例：
            # 基本查询
            response = api.read(
                endpoint="/invoke/planning-api/method/understanding/read",
                user_id="user123",
                data=["我喜欢吃肉"]
            )

            # 带检索选项的查询
            response = api.read(
                endpoint="/invoke/planning-api/method/understanding/read",
                user_id="user123",
                data=["我喜欢吃肉"],
                retrieval_options={
                    "limit": 10,
                    "threshold": 0.8
                }
            )

            # 使用自定义headers
            custom_headers = {"Authorization": "token xxx"}
            response = api.read(
                endpoint="/invoke/planning-api/method/understanding/read",
                user_id="user123",
                data=["我喜欢吃肉"],
                headers=custom_headers
            )

        注意：
            - user_id必须有效
            - data必须是列表格式
            - 成功时返回200，参数错误时返回400
            - 如果check_status_code=False，不验证状态码，直接返回响应
        """
        payload = {
            "user_id": user_id,
            "data": data
        }
        if retrieval_options:
            payload["retrieval_options"] = retrieval_options

        logger.info(
            f"调用read接口 - endpoint: {endpoint}, user_id: {user_id}"
            + (f", timeout: {timeout}s" if timeout is not None else "")
        )
        client = build_api_client(
            headers=headers,
            timeout=timeout,
            use_env_token=use_env_token,
        )
        response = client.post(endpoint, json=payload)

        if check_status_code and response.status_code not in [200, 400]:
            logger.error(f"read接口返回异常状态码: {response.status_code}")
            raise InvalidResponseError(
                message=f"read接口返回异常状态码: {response.status_code}",
                response_data={"status_code": response.status_code, "body": response.text}
            )

        logger.info(f"read接口调用成功 - 状态码: {response.status_code}")
        return response
