"""
HTTP客户端模块

本模块封装了requests库，提供了统一的HTTP请求接口，支持：
- 超时控制：防止请求长时间挂起
- 异常处理：将requests异常转换为自定义异常
- 配置驱动：从配置文件读取超时等参数
- Session复用：提升性能，保持连接池

核心功能：
    1. 超时控制：默认30秒超时，可配置
    2. SSL验证：支持开启/关闭SSL证书验证
    3. 日志记录：详细记录请求、响应、异常信息
    4. 异常转换：将requests异常转换为自定义异常

使用示例：
    from src.utils.http_client import http_client
    
    # GET请求
    response = http_client.get("/api/users", params={"page": 1})
    
    # POST请求
    response = http_client.post("/api/users", json={"name": "张三"})
    
    # 自定义配置
    custom_client = HTTPClient(
        base_url="https://api.example.com",
        timeout=60
    )
"""

import requests
from requests.adapters import HTTPAdapter
from typing import Optional, Dict, Any, Union, Tuple
from urllib.parse import urlparse
from src.utils.exceptions import (
    HTTPRequestError,
    ConnectionError,
    TimeoutError
)
from src.utils.logger import get_logger

logger = get_logger("http_client")

_RequestTimeout = Union[float, Tuple[float, float]]


def _timeout_seconds_for_error(timeout: Optional[_RequestTimeout]) -> Optional[float]:
    """标量直接返回; requests 的 (connect, read) 元组取 read, 便于与 Read timed out 对齐。"""
    if timeout is None:
        return None
    if isinstance(timeout, (int, float)):
        return float(timeout)
    if isinstance(timeout, tuple) and len(timeout) >= 2:
        return float(timeout[1])
    return None


class HTTPClient:
    """
    HTTP客户端类
    
    封装requests.Session，提供统一的HTTP请求接口。
    支持超时控制、异常处理等高级功能。
    
    属性：
        base_url: API基础URL
        timeout: 请求超时时间（秒）
        verify_ssl: 是否验证SSL证书
        session: requests.Session实例
        default_headers: 默认请求头
    
    配置优先级：
        参数 > 配置文件 > 默认值
    
    示例：
        # 使用默认配置
        client = HTTPClient()
        
        # 自定义配置
        client = HTTPClient(
            base_url="https://api.example.com",
            timeout=60,
            verify_ssl=True
        )
    """

    def __init__(
        self,
        base_url: str = None,
        headers: Optional[Dict] = None,
        timeout: float = None,
        verify_ssl: bool = None,
        merge_headers: bool = True
    ):
        """
        初始化HTTP客户端

        Args:
            base_url: API基础URL，如果不指定则从配置文件读取
            headers: 自定义请求头。如果 merge_headers=False，则完全替换默认headers。
            timeout: 请求超时时间（秒），默认从配置文件读取（30秒）
            verify_ssl: 是否验证SSL证书，默认从配置文件读取（False）
            merge_headers: 是否合并默认headers，默认为True。如果设为False，则完全替换默认headers。

        配置加载顺序：
            1. 检查传入参数
            2. 从config/http_config.yaml读取配置
            3. 使用硬编码的默认值

        注意：
            - 如果没有提供 headers，将使用空字典作为默认headers
            - 所有headers现在必须通过测试数据YAML文件提供
        """
        from src.config.env_config import env_config as _env

        self.base_url = base_url or _env.BASE_URL
        self.timeout = (
            timeout if timeout is not None else float(_env.TIMEOUT)
        )
        self.verify_ssl = (
            verify_ssl if verify_ssl is not None else _env.VERIFY_SSL
        )

        self.session = requests.Session()
        if headers is not None and not merge_headers:
            self.default_headers = headers
        elif headers is not None:
            self.default_headers = headers
        else:
            self.default_headers = {}
        self.session.headers.update(self.default_headers)

        adapter = HTTPAdapter()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        logger.info(
            f"[http_client] HTTPClient初始化完成 | base_url: {self.base_url} | "
            f"timeout: {self.timeout}s | verify_ssl: {self.verify_ssl} | "
            f"TEST_ENV: {_env.ENV}"
        )

    def _build_url(self, endpoint: str) -> str:
        """
        构建完整的请求URL
        
        Args:
            endpoint: API端点路径，如"/api/users"
        
        Returns:
            完整的URL，如"https://api.example.com/api/users"
        
        示例：
            url = self._build_url("/api/users")
            # 返回: "https://plan-dev.api.brain.ai/v1.0/api/users"
        """
        return f"{self.base_url}{endpoint}"

    def _handle_request_exception(
        self,
        exception: Exception,
        method: str,
        url: str,
        request_timeout: Optional[_RequestTimeout] = None,
    ):
        """
        处理请求异常，将requests异常转换为自定义异常
        
        Args:
            exception: 原始异常对象
            method: HTTP方法（GET/POST/PUT/DELETE）
            url: 请求URL
        
        Raises:
            TimeoutError: 请求超时时抛出
            ConnectionError: 网络连接失败时抛出
            HTTPRequestError: HTTP请求异常时抛出
            Exception: 其他未知异常
        
        异常转换规则：
            requests.exceptions.Timeout -> TimeoutError
            requests.exceptions.ConnectionError -> ConnectionError
            requests.exceptions.RequestException -> HTTPRequestError
            其他异常 -> 原样抛出
        """
        if isinstance(exception, requests.exceptions.Timeout):
            logger.error(f"请求超时 - {method} {url}: {str(exception)}")
            t_err = _timeout_seconds_for_error(request_timeout)
            if t_err is None:
                t_err = float(self.timeout)
            raise TimeoutError(
                message=f"{method} {url} 请求超时",
                timeout=t_err
            )
        elif isinstance(exception, requests.exceptions.ConnectionError):
            logger.error(f"网络连接失败 - {method} {url}: {str(exception)}")
            raise ConnectionError(
                message=f"{method} {url} 网络连接失败",
                original_exception=exception
            )
        elif isinstance(exception, requests.exceptions.RequestException):
            logger.error(f"HTTP请求异常 - {method} {url}: {str(exception)}")
            raise HTTPRequestError(
                message=f"{method} {url} 请求失败: {str(exception)}"
            )
        else:
            logger.error(f"未知异常 - {method} {url}: {str(exception)}")
            raise exception

    def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法（GET/POST/PUT/DELETE）
            url: 完整的请求URL
            **kwargs: 传递给requests.request的其他参数
        
        Returns:
            requests.Response: 响应对象
        
        Raises:
            TimeoutError: 请求超时时抛出
            ConnectionError: 网络连接失败时抛出
            HTTPRequestError: HTTP请求异常时抛出
        """
        try:
            kwargs.setdefault('timeout', self.timeout)
            kwargs.setdefault('verify', self.verify_ssl)
            request_timeout = kwargs.get("timeout")

            logger.debug(f"发送请求 - {method} {url}")
            response = self.session.request(method, url, **kwargs)

            if response.status_code >= 400:
                logger.warning(
                    f"请求返回错误状态码 {response.status_code} - {method} {url}"
                )

            return response

        except Exception as e:
            self._handle_request_exception(
                e,
                method,
                url,
                request_timeout=request_timeout,
            )

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """
        发送POST请求
        
        Args:
            endpoint: API端点路径，如"/api/users"
            json: 请求体JSON数据
            params: URL查询参数
            **kwargs: 传递给requests.request的其他参数
        
        Returns:
            requests.Response: 响应对象
        
        示例：
            response = http_client.post(
                "/api/users",
                json={"name": "张三", "age": 25}
            )
        """
        url = self._build_url(endpoint)
        logger.info(f"POST请求 - {url}")
        if json:
            logger.debug(f"请求体: {json}")
        return self._request("POST", url, json=json, params=params, **kwargs)

    def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """
        发送GET请求
        
        Args:
            endpoint: API端点路径，如"/api/users"
            params: URL查询参数
            **kwargs: 传递给requests.request的其他参数
        
        Returns:
            requests.Response: 响应对象
        
        示例：
            response = http_client.get(
                "/api/users",
                params={"page": 1, "size": 10}
            )
        """
        url = self._build_url(endpoint)
        logger.info(f"GET请求 - {url}")
        return self._request("GET", url, params=params, **kwargs)

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        发送PUT请求
        
        Args:
            endpoint: API端点路径，如"/api/users/123"
            json: 请求体JSON数据
            **kwargs: 传递给requests.request的其他参数
        
        Returns:
            requests.Response: 响应对象
        
        示例：
            response = http_client.put(
                "/api/users/123",
                json={"name": "李四", "age": 30}
            )
        """
        url = self._build_url(endpoint)
        logger.info(f"PUT请求 - {url}")
        if json:
            logger.debug(f"请求体: {json}")
        return self._request("PUT", url, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """
        发送DELETE请求
        
        Args:
            endpoint: API端点路径，如"/api/users/123"
            **kwargs: 传递给requests.request的其他参数
        
        Returns:
            requests.Response: 响应对象
        
        示例：
            response = http_client.delete("/api/users/123")
        """
        url = self._build_url(endpoint)
        logger.info(f"DELETE请求 - {url}")
        return self._request("DELETE", url, **kwargs)

    def close(self):
        """
        关闭HTTP Session
        
        释放连接池资源，通常在测试结束时调用。
        
        示例：
            http_client.close()
        """
        logger.info("关闭HTTP Session")
        self.session.close()


def resolve_api_headers(
    headers: Optional[Dict[str, Any]] = None,
    use_env_token: bool = True,
) -> Dict[str, Any]:
    """
    解析 API 请求最终生效的请求头。

    规则:
    - use_env_token=True: 自动注入当前环境 token
    - use_env_token=False: 不注入默认 token
    - headers 如显式传入 Authorization: 使用调用方传入值覆盖默认 token
    """
    from src.config.env_config import env_config as _env

    resolved_headers: Dict[str, Any] = {}
    auth_source = "disabled"

    if use_env_token:
        env_token = _env.TOKEN
        if env_token:
            resolved_headers["Authorization"] = f"token {env_token}"
            auth_source = "env_default"
        else:
            auth_source = "env_missing"
    if headers is not None:
        resolved_headers.update(dict(headers))
    if "Authorization" in resolved_headers and headers is not None:
        auth_source = "custom"

    host = urlparse(_env.BASE_URL).netloc
    if host:
        resolved_headers.setdefault("Host", host)
    resolved_headers.setdefault("Content-Type", "application/json")

    logger.info(
        f"[ApiAuth] build_api_client | env={_env.ENV} | use_env_token={use_env_token} | headers_provided={headers is not None} | "
        f"has_authorization={'Authorization' in resolved_headers} | "
        f"host={resolved_headers.get('Host')} | content_type={resolved_headers.get('Content-Type')} | auth_source={auth_source}"
    )
    return resolved_headers


def build_api_client(
    headers: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
    use_env_token: bool = True,
) -> HTTPClient:
    """
    构造 API 请求客户端。
    """
    resolved_headers = resolve_api_headers(headers=headers, use_env_token=use_env_token)
    return HTTPClient(headers=resolved_headers, timeout=timeout, merge_headers=False)


http_client = HTTPClient()