"""
AI Phone Planning API封装模块

本模块封装了AI Phone Planning相关的API接口，提供统一的API调用接口。
主要功能：
- find：查询planning列表

设计原则：
1. 单一职责：每个方法只负责一个API调用
2. 错误处理：使用@handle_api_errors装饰器统一处理异常
3. 日志记录：详细记录API调用过程
4. 响应验证：验证响应状态码，确保数据有效性

使用示例：
    from src.api.ai_phone_planning_api import AIPhonePlanningAPI

    # 查询planning列表
    api = AIPhonePlanningAPI()
    response = api.find()

    # 使用自定义headers
    custom_headers = {"Authorization": "token xxx"}
    response = api.find(headers=custom_headers)

    # 允许非200状态码
    response = api.find(check_status_code=False)
"""

from src.utils.http_client import build_api_client
from src.utils.error_handler import handle_api_errors
from src.utils.exceptions import InvalidResponseError
from src.utils.logger import get_logger
from typing import Optional, Dict, Any

logger = get_logger("ai_phone_planning_api")


class AIPhonePlanningAPI:
    """
    AI Phone Planning API封装类

    封装了AI Phone Planning相关的所有API接口，提供统一的调用方式。
    所有方法都使用@handle_api_errors装饰器进行异常处理。

    方法：
        find() - 查询planning列表

    使用示例：
        api = AIPhonePlanningAPI()

        # 查询planning列表
        response = api.find()

        # 使用自定义headers
        custom_headers = {"Authorization": "token xxx"}
        response = api.find(headers=custom_headers)

        # 允许非200状态码
        response = api.find(check_status_code=False)
    """

    HTTP_METHOD_FIND = "GET"
    PATH_FIND = "/planning-api/method/ai_phone/planning/find"

    @staticmethod
    @handle_api_errors
    def find(
        headers: Optional[Dict[str, Any]] = None,
        check_status_code: bool = True,
        use_env_token: bool = True,
    ):
        """
        查询planning列表

        获取当前用户的planning会话列表。

        Args:
            headers: 自定义请求头（可选）。如果提供，将使用自定义headers代替默认headers。
            check_status_code: 是否验证状态码，默认为True。如果设为False，则允许非200状态码（如400错误）。

        Returns:
            requests.Response: 响应对象，包含planning列表

        Raises:
            InvalidResponseError: 当响应状态码不是200时抛出（除非check_status_code=False）

        示例：
            response = api.find()
            print(response.json())

            # 使用自定义headers
            custom_headers = {"Authorization": "token xxx"}
            response = api.find(headers=custom_headers)

        注意：
            - 返回当前用户的planning会话列表
            - 成功时返回200
            - 如果check_status_code=False，不验证状态码，直接返回响应
        """
        logger.info("开始查询planning列表")
        path = AIPhonePlanningAPI.PATH_FIND
        client = build_api_client(headers=headers, use_env_token=use_env_token)
        response = client.get(path)

        if check_status_code and response.status_code != 200:
            logger.error(f"find接口返回异常状态码: {response.status_code}")
            raise InvalidResponseError(
                message=f"find接口返回异常状态码: {response.status_code}",
                response_data={"status_code": response.status_code, "body": response.text}
            )

        logger.info(f"find接口调用成功 - 状态码: {response.status_code}")
        return response
