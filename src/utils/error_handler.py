"""
错误处理装饰器模块

本模块提供了一系列装饰器，用于统一处理测试过程中的异常和错误。
主要功能包括：
- 自动捕获异常并记录日志
- 自动将异常信息附加到Allure报告
- 提供测试失败自动重试机制
- 提供错误跳过机制
- 自动记录测试步骤

可用装饰器：
    1. @handle_api_errors - API错误处理装饰器
    2. @retry_on_failure(max_retries, delay) - 失败重试装饰器
    3. @skip_on_error(error_type, reason) - 错误跳过装饰器
    4. @log_test_step(step_name) - 测试步骤日志装饰器

使用示例：
    from src.utils.error_handler import handle_api_errors, retry_on_failure
    
    # 使用API错误处理装饰器
    @handle_api_errors
    def test_api_call():
        response = http_client.get("/api/users")
        assert response.status_code == 200
    
    # 使用失败重试装饰器
    @retry_on_failure(max_retries=3, delay=1.0)
    def test_unstable_api():
        # 这个测试失败后会自动重试3次
        response = http_client.get("/api/unstable")
        assert response.status_code == 200
"""

import functools
from src.utils.logger import get_logger
from src.utils.exceptions import (
    APIAutomationException,
    ConnectionError,
    TimeoutError,
    InvalidResponseError,
    RetryExhaustedError
)
import allure
import pytest

logger = get_logger("error_handler")


def handle_api_errors(func):
    """
    API错误处理装饰器
    
    自动捕获API自动化测试异常，记录日志并附加到Allure报告。
    这是API层方法的标准装饰器，确保所有异常都被正确处理。
    
    功能：
        1. 捕获APIAutomationException及其子类异常
        2. 记录详细的错误日志
        3. 将异常信息附加到Allure报告
        4. 重新抛出异常，保持异常链
    
    Args:
        func: 被装饰的函数
    
    Returns:
        装饰后的函数
    
    Raises:
        APIAutomationException: API自动化测试异常
        Exception: 其他未预期的异常
    
    使用示例：
        @handle_api_errors
        def get_user(user_id):
            response = http_client.get(f"/api/users/{user_id}")
            if response.status_code != 200:
                raise HTTPRequestError(
                    message="获取用户失败",
                    status_code=response.status_code
                )
            return response.json()
    
    注意：
        - 此装饰器会重新抛出异常，调用方需要处理异常
        - 异常信息会自动记录到日志和Allure报告
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIAutomationException as e:
            logger.error(f"API自动化测试异常: {str(e)}")
            allure.attach(
                str(e),
                name="异常信息",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        except Exception as e:
            logger.error(f"未预期的异常: {str(e)}", exc_info=True)
            allure.attach(
                str(e),
                name="未预期异常",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    失败重试装饰器
    
    当测试失败时自动重试，适用于不稳定的测试场景。
    常用于网络不稳定、服务偶尔超时等情况。
    
    Args:
        max_retries: 最大重试次数，默认3次
        delay: 重试间隔时间（秒），默认1.0秒
    
    Returns:
        装饰器函数
    
    Raises:
        Exception: 最后一次失败时抛出的异常
    
    使用示例：
        # 重试3次，每次间隔1秒
        @retry_on_failure(max_retries=3, delay=1.0)
        def test_unstable_api():
            response = http_client.get("/api/unstable")
            assert response.status_code == 200
        
        # 重试5次，每次间隔2秒
        @retry_on_failure(max_retries=5, delay=2.0)
        def test_flaky_network():
            # 测试不稳定的网络连接
            response = http_client.get("/api/data")
            assert response.json()["status"] == "success"
    
    注意：
        - 重试次数不包括第一次执行
        - 每次重试都会记录警告日志
        - 最后一次失败会抛出异常
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"测试失败, 准备第{attempt + 1}次重试: {str(e)}"
                        )
                        import time
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"测试失败且已重试{max_retries}次: {str(e)}"
                        )
            raise last_exception
        return wrapper
    return decorator


def skip_on_error(error_type: type = None, reason: str = "跳过错误"):
    """
    错误跳过装饰器
    
    当指定类型的异常发生时，跳过测试而不是标记为失败。
    适用于某些已知问题或依赖外部服务的测试。
    
    Args:
        error_type: 要跳过的异常类型，如ConnectionError、TimeoutError等
        reason: 跳过原因，会显示在测试报告中
    
    Returns:
        装饰器函数
    
    使用示例：
        # 当网络连接失败时跳过测试
        @skip_on_error(error_type=ConnectionError, reason="网络不可用")
        def test_external_api():
            response = http_client.get("https://external-api.com/data")
            assert response.status_code == 200
        
        # 当超时时跳过测试
        @skip_on_error(error_type=TimeoutError, reason="服务响应超时")
        def test_slow_service():
            response = http_client.get("/api/slow-service")
            assert response.json()["status"] == "ok"
    
    注意：
        - 只有指定的异常类型才会跳过
        - 其他异常仍然会导致测试失败
        - 跳过的测试在报告中标记为SKIPPED
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type as e:
                logger.warning(f"跳过测试 - {reason}: {str(e)}")
                import pytest
                pytest.skip(reason)
        return wrapper
    return decorator


def log_test_step(step_name: str):
    """
    测试步骤日志装饰器
    
    自动记录测试步骤到日志和Allure报告，提升测试报告的可读性。
    常用于标记测试中的关键步骤。
    
    Args:
        step_name: 步骤名称，会显示在日志和报告中
    
    Returns:
        装饰器函数
    
    使用示例：
        @log_test_step("准备测试数据")
        def prepare_test_data():
            # 准备测试数据的逻辑
            return {"user_id": 123, "name": "张三"}
        
        @log_test_step("发送API请求")
        def send_api_request(data):
            response = http_client.post("/api/users", json=data)
            return response
        
        @log_test_step("验证响应结果")
        def verify_response(response):
            assert response.status_code == 200
            assert response.json()["success"] is True
    
    注意：
        - 步骤名称应该简洁明了
        - 步骤会在Allure报告中显示为折叠项
        - 日志中会记录步骤的开始和结束
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"执行步骤: {step_name}")
            with allure.step(step_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class ExceptionHandler:
    """
    测试异常处理上下文管理器
    
    统一处理测试过程中的各种异常,包括网络异常、重试耗尽、响应无效等。
    自动记录日志、附加到Allure报告,并根据异常类型决定是否调用pytest.fail或重新抛出。
    
    使用场景:
        在测试方法中使用with语句包裹可能抛出异常的代码块。
    
    使用示例:
        def test_api_call(self):
            with ExceptionHandler(self.logger, self.request):
                response = self.api.get("/users")
                assert response.status_code == 200
    
    异常处理策略:
        1. ConnectionError/TimeoutError: 网络异常,调用pytest.fail终止测试
        2. RetryExhaustedError: 重试耗尽,调用pytest.fail终止测试
        3. InvalidResponseError: 响应无效,调用pytest.fail终止测试
        4. APIAutomationException: API异常,调用pytest.fail终止测试
        5. Exception: 未预期异常,记录日志后重新抛出
    
    注意:
        - 需要传入logger对象用于记录日志
        - 需要传入request对象用于访问测试上下文(可选)
    """
    
    def __init__(self, logger, request=None):
        """
        初始化异常处理器
        
        Args:
            logger: 日志记录器对象
            request: pytest的request fixture对象(可选)
        """
        self.logger = logger
        self.request = request
    
    def __enter__(self):
        """进入上下文"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文时处理异常
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
        
        Returns:
            True表示抑制异常，False或None表示重新抛出异常
        """
        if exc_type is None:
            return False

        if exc_type in (ConnectionError, TimeoutError):
            self.logger.error(f"网络异常导致测试失败: {str(exc_val)}")
            allure.attach(str(exc_val), name="网络异常", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"网络异常: {str(exc_val)}")
            return True
        
        elif exc_type == RetryExhaustedError:
            self.logger.error(f"重试耗尽导致测试失败: {str(exc_val)}")
            allure.attach(str(exc_val), name="重试耗尽", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"重试耗尽: {str(exc_val)}")
            return True
        
        elif exc_type == InvalidResponseError:
            self.logger.error(f"响应数据无效: {str(exc_val)}")
            allure.attach(str(exc_val), name="响应无效", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"响应数据无效: {str(exc_val)}")
            return True
        
        elif exc_type == APIAutomationException:
            self.logger.error(f"API自动化测试异常: {str(exc_val)}")
            allure.attach(str(exc_val), name="API异常", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"API异常: {str(exc_val)}")
            return True

        elif exc_type == AssertionError:
            self.logger.error(f"断言失败: {str(exc_val)}")
            allure.attach(str(exc_val), name="断言失败", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"断言失败: {str(exc_val)}")
            return True
        
        elif exc_type == Exception:
            self.logger.error(f"未预期的异常: {str(exc_val)}", exc_info=True)
            allure.attach(str(exc_val), name="未预期异常", attachment_type=allure.attachment_type.TEXT)
            return False
        
        return False
