"""
Planning API封装模块

本模块封装了Planning相关的API接口，提供统一的API调用接口。
主要功能：
- conductor接口：执行规划任务，支持流式响应
- delete接口：删除会话

设计原则：
1. 单一职责：每个方法只负责一个API调用
2. 错误处理：使用@handle_api_errors装饰器统一处理异常
3. 日志记录：详细记录API调用过程
4. 响应验证：验证响应状态码，确保数据有效性

使用示例：
    from src.api.planning_api import PlanningAPI

    # 执行规划任务
    api = PlanningAPI()
    response = api.conductor(
        endpoint="/invoke/planning-api/method/v2/conductor",
        data={
            "session_id": "",
            "focus_id": "auto",
            "message_id": "",
            "query": "今天天气如何",
            "stream": True,
            "pubsub_topic": ""
        }
    )

    # 删除会话
    response = api.delete(
        endpoint="/invoke/planning-api/method/ai_phone/planning/delete",
        session_id="57b05331-61e5-4688-af77-d1505e1cbf5a"
    )
"""

from src.utils.http_client import build_api_client
from src.utils.error_handler import handle_api_errors
from src.utils.exceptions import InvalidResponseError
from src.utils.logger import get_logger
from typing import Optional, Dict, Any

logger = get_logger("planning_api")


class PlanningAPI:
    """
    Planning API封装类

    封装了Planning相关的所有API接口，提供统一的调用方式。
    所有方法都使用@handle_api_errors装饰器进行异常处理。

    方法：
        conductor(endpoint, data, headers, check_status_code) - 执行规划任务
        delete(endpoint, session_id, headers, check_status_code) - 删除会话

    使用示例：
        api = PlanningAPI()

        # 执行规划任务
        response = api.conductor(
            endpoint="/invoke/planning-api/method/v2/conductor",
            data={
                "session_id": "",
                "focus_id": "auto",
                "message_id": "",
                "query": "今天天气如何",
                "stream": True,
                "pubsub_topic": ""
            }
        )

        # 删除会话
        response = api.delete(
            endpoint="/invoke/planning-api/method/ai_phone/planning/delete",
            session_id="57b05331-61e5-4688-af77-d1505e1cbf5a"
        )

        # 使用自定义headers
        custom_headers = {"Authorization": "token xxx"}
        response = api.conductor(
            endpoint="/invoke/planning-api/method/v2/conductor",
            data={...},
            headers=custom_headers
        )
    """

    @staticmethod
    @handle_api_errors
    def conductor(
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None,
        check_status_code: bool = True,
        use_env_token: bool = True,
    ):
        """
        执行规划任务

        发送规划任务请求，支持流式响应。

        Args:
            endpoint: API端点路径，如"/invoke/planning-api/method/v2/conductor"
            data: 请求数据，包含session_id、focus_id、message_id、query、stream、pubsub_topic等字段
            headers: 自定义请求头（可选）。如果提供，将使用自定义headers代替默认headers。
            check_status_code: 是否验证状态码，默认为True。如果设为False，则允许非200状态码。

        Returns:
            requests.Response: 响应对象，包含规划结果

        Raises:
            InvalidResponseError: 当响应状态码不是200时抛出（除非check_status_code=False）

        示例：
            response = api.conductor(
                endpoint="/invoke/planning-api/method/v2/conductor",
                data={
                    "session_id": "",
                    "focus_id": "auto",
                    "message_id": "",
                    "query": "今天天气如何",
                    "stream": True,
                    "pubsub_topic": ""
                }
            )

            # 使用自定义headers
            custom_headers = {"Authorization": "token xxx"}
            response = api.conductor(
                endpoint="/invoke/planning-api/method/v2/conductor",
                data={...},
                headers=custom_headers
            )

        注意：
            - data必须是字典格式
            - session_id、pubsub_topic、message_id会自动生成
            - 成功时返回200
            - 如果check_status_code=False，不验证状态码，直接返回响应
        """
        logger.info(f"调用conductor接口 - endpoint: {endpoint}")
        client = build_api_client(headers=headers, use_env_token=use_env_token)
        response = client.post(endpoint, json=data)

        if check_status_code and response.status_code != 200:
            logger.error(f"conductor接口返回异常状态码: {response.status_code}")
            raise InvalidResponseError(
                message=f"conductor接口返回异常状态码: {response.status_code}",
                response_data={"status_code": response.status_code, "body": response.text}
            )

        logger.info(f"conductor接口调用成功 - 状态码: {response.status_code}")
        return response

    @staticmethod
    @handle_api_errors
    def delete(
        endpoint: str,
        session_id: str,
        headers: Optional[Dict[str, Any]] = None,
        check_status_code: bool = True,
        use_env_token: bool = True,
    ):
        """
        删除会话

        根据session_id删除指定的会话。

        Args:
            endpoint: API端点路径，如"/invoke/planning-api/method/ai_phone/planning/delete"
            session_id: 会话ID，用于标识要删除的会话
            headers: 自定义请求头（可选）。如果提供，将使用自定义headers代替默认headers。
            check_status_code: 是否验证状态码，默认为True。如果设为False，则允许非200状态码。

        Returns:
            requests.Response: 响应对象，包含删除结果

        Raises:
            InvalidResponseError: 当响应状态码不是200时抛出（除非check_status_code=False）

        示例：
            response = api.delete(
                endpoint="/invoke/planning-api/method/ai_phone/planning/delete",
                session_id="57b05331-61e5-4688-af77-d1505e1cbf5a"
            )

            # 使用自定义headers
            custom_headers = {"Authorization": "token xxx"}
            response = api.delete(
                endpoint="/invoke/planning-api/method/ai_phone/planning/delete",
                session_id="57b05331-61e5-4688-af77-d1505e1cbf5a",
                headers=custom_headers
            )

        注意：
            - session_id必须有效
            - 成功时返回200
            - 如果check_status_code=False，不验证状态码，直接返回响应
        """
        endpoint_with_params = f"{endpoint}?session_id={session_id}"
        logger.info(f"调用delete接口 - endpoint: {endpoint_with_params}")
        client = build_api_client(headers=headers, use_env_token=use_env_token)
        response = client.post(endpoint_with_params)

        if check_status_code and response.status_code != 200:
            logger.error(f"delete接口返回异常状态码: {response.status_code}")
            raise InvalidResponseError(
                message=f"delete接口返回异常状态码: {response.status_code}",
                response_data={"status_code": response.status_code, "body": response.text}
            )

        logger.info(f"delete接口调用成功 - 状态码: {response.status_code}")
        return response
