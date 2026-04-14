"""
用户信息 API封装模块

本模块封装了用户信息相关的API接口，提供统一的API调用接口。
主要功能：
- get_current_user：获取当前用户信息

设计原则：
1. 单一职责：每个方法只负责一个API调用
2. 错误处理：使用@handle_api_errors装饰器统一处理异常
3. 日志记录：详细记录API调用过程
4. 响应验证：验证响应状态码，确保数据有效性

使用示例：
    from src.api.user_api import UserAPI

    # 获取当前用户信息
    api = UserAPI()
    response = api.get_current_user()

    # 使用自定义headers获取用户信息
    custom_headers = {
        "Authorization": "token xxx",
        "Content-Type": "application/json"
    }
    response = api.get_current_user(headers=custom_headers)

    # 获取用户信息并允许非200状态码
    response = api.get_current_user(check_status_code=False)
"""

from src.utils.http_client import build_api_client
from src.utils.error_handler import handle_api_errors
from src.utils.exceptions import InvalidResponseError
from src.utils.logger import get_logger
from typing import Optional, Dict, Any

logger = get_logger("user_api")


class UserAPI:
    """
    用户信息 API封装类

    封装了用户信息相关的所有API接口，提供统一的调用方式。
    所有方法都使用@handle_api_errors装饰器进行异常处理。

    方法：
        get_current_user() - 获取当前用户信息

    使用示例：
        api = UserAPI()

        # 获取当前用户信息
        response = api.get_current_user()

        # 使用自定义headers
        custom_headers = {"Authorization": "token xxx"}
        response = api.get_current_user(headers=custom_headers)

        # 允许非200状态码（如400错误）
        response = api.get_current_user(check_status_code=False)
    """

    HTTP_METHOD_GET_CURRENT_USER = "GET"
    PATH_GET_CURRENT_USER = "/userly/method/users/me.json"

    @staticmethod
    @handle_api_errors
    def get_current_user(
        headers: Optional[Dict[str, Any]] = None,
        check_status_code: bool = True,
        use_env_token: bool = True,
    ):
        """
        获取当前登录用户的信息

        Args:
            headers: 自定义请求头（可选）。如果提供，将使用自定义headers代替默认headers。
            check_status_code: 是否验证状态码，默认为True。如果设为False，则允许非200状态码（如400错误）。

        Returns:
            requests.Response: 响应对象，包含用户信息

        Raises:
            InvalidResponseError: 当响应状态码不是200时抛出（除非check_status_code=False）

        示例：
            response = api.get_current_user()
            print(response.json())

            # 使用自定义headers
            custom_headers = {"Authorization": "token xxx"}
            response = api.get_current_user(headers=custom_headers)

            # 允许400状态码
            response = api.get_current_user(check_status_code=False)

        注意：
            - 返回当前登录用户的所有信息
            - 成功时返回200
            - 如果提供了headers参数，将使用自定义headers
            - check_status_code=False时，不验证状态码，直接返回响应
        """
        logger.info("开始获取当前用户信息")
        path = UserAPI.PATH_GET_CURRENT_USER
        client = build_api_client(headers=headers, use_env_token=use_env_token)
        response = client.get(path)

        if check_status_code and response.status_code != 200:
            logger.error(f"get_current_user接口返回异常状态码: {response.status_code}")
            raise InvalidResponseError(
                message=f"get_current_user接口返回异常状态码: {response.status_code}",
                response_data={"status_code": response.status_code, "body": response.text}
            )

        logger.info(f"get_current_user接口调用成功 - 状态码: {response.status_code}")
        return response
