"""
自定义异常模块

本模块定义了API自动化测试框架中使用的所有自定义异常类。
所有异常都继承自APIAutomationException基类，形成完整的异常层次结构。

异常层次结构：
    APIAutomationException (基类)
    ├── HTTPRequestError        - HTTP请求异常
    ├── ConnectionError         - 网络连接异常
    ├── TimeoutError           - 请求超时异常
    ├── InvalidResponseError   - 响应数据无效异常
    ├── ConfigurationError     - 配置错误异常
    └── TestDataError          - 测试数据错误异常

使用示例：
    from utils.exceptions import HTTPRequestError, ConnectionError
    
    # 抛出HTTP请求异常
    raise HTTPRequestError(
        message="请求失败",
        status_code=500,
        response_text="Internal Server Error"
    )
    
    # 捕获异常
    try:
        response = http_client.get("/api/test")
    except ConnectionError as e:
        logger.error(f"网络连接失败: {str(e)}")
"""


class APIAutomationException(Exception):
    """
    API自动化测试基础异常类
    
    所有自定义异常的基类，提供统一的异常处理接口。
    继承自Python内置的Exception类。
    
    使用场景：
        当需要抛出一个通用的API自动化测试异常时使用。
    
    示例：
        raise APIAutomationException("测试执行失败")
    """
    pass


class HTTPRequestError(APIAutomationException):
    """
    HTTP请求异常
    
    当HTTP请求失败时抛出此异常，包含详细的错误信息。
    
    属性：
        message: 错误消息描述
        status_code: HTTP状态码（可选）
        response_text: 响应内容（可选，最多显示前200个字符）
    
    使用场景：
        - HTTP状态码为4xx或5xx时
        - 请求返回非预期结果时
        - 响应内容解析失败时
    
    示例：
        raise HTTPRequestError(
            message="用户认证失败",
            status_code=401,
            response_text='{"error": "Invalid token"}'
        )
    """

    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        """
        初始化HTTP请求异常
        
        Args:
            message: 错误消息描述
            status_code: HTTP状态码，如404、500等
            response_text: 响应内容文本，会在错误信息中截取前200个字符
        """
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self.message)

    def __str__(self):
        """
        返回格式化的错误信息
        
        Returns:
            格式化的错误字符串，包含状态码和响应内容（如果有）
        """
        error_msg = f"HTTP请求失败: {self.message}"
        if self.status_code:
            error_msg += f", 状态码: {self.status_code}"
        if self.response_text:
            error_msg += f", 响应内容: {self.response_text[:200]}"
        return error_msg


class ConnectionError(APIAutomationException):
    """
    网络连接异常
    
    当网络连接失败时抛出此异常，通常是由于网络不可达、DNS解析失败等原因。
    
    属性：
        message: 错误消息描述
        original_exception: 原始异常对象（可选），用于追踪根本原因
    
    使用场景：
        - 无法连接到服务器
        - DNS解析失败
        - 网络超时
        - 代理连接失败
    
    示例：
        try:
            response = requests.get("https://api.example.com")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                message="无法连接到API服务器",
                original_exception=e
            )
    """

    def __init__(self, message: str, original_exception: Exception = None):
        """
        初始化网络连接异常
        
        Args:
            message: 错误消息描述
            original_exception: 原始异常对象，用于保留异常链
        """
        self.message = message
        self.original_exception = original_exception
        super().__init__(self.message)

    def __str__(self):
        """
        返回格式化的错误信息
        
        Returns:
            格式化的错误字符串，包含原始异常信息（如果有）
        """
        error_msg = f"网络连接失败: {self.message}"
        if self.original_exception:
            error_msg += f", 原始异常: {str(self.original_exception)}"
        return error_msg


class TimeoutError(APIAutomationException):
    """
    请求超时异常
    
    当HTTP请求超过设定的超时时间时抛出此异常。
    
    属性：
        message: 错误消息描述
        timeout: 超时时间（秒），可选
    
    使用场景：
        - 请求超时未响应
        - 读取响应超时
        - 连接超时
    
    示例：
        raise TimeoutError(
            message="API响应超时",
            timeout=30.0
        )
    """

    def __init__(self, message: str, timeout: float = None):
        """
        初始化请求超时异常
        
        Args:
            message: 错误消息描述
            timeout: 超时时间（秒），用于记录配置的超时时间
        """
        self.message = message
        self.timeout = timeout
        super().__init__(self.message)

    def __str__(self):
        """
        返回格式化的错误信息
        
        Returns:
            格式化的错误字符串，包含超时时间（如果有）
        """
        error_msg = f"请求超时: {self.message}"
        if self.timeout:
            error_msg += f", 超时时间: {self.timeout}秒"
        return error_msg


class InvalidResponseError(APIAutomationException):
    """
    响应数据无效异常
    
    当API响应数据不符合预期格式或缺少必要字段时抛出此异常。
    
    属性：
        message: 错误消息描述
        response_data: 响应数据字典（可选），会在错误信息中截取前200个字符
    
    使用场景：
        - 响应JSON解析失败
        - 缺少必要字段
        - 数据类型不匹配
        - 响应格式不符合预期
    
    示例：
        response = http_client.get("/api/user")
        data = response.json()
        if "user_id" not in data:
            raise InvalidResponseError(
                message="响应缺少user_id字段",
                response_data=data
            )
    """

    def __init__(self, message: str, response_data: dict = None):
        """
        初始化响应数据无效异常
        
        Args:
            message: 错误消息描述
            response_data: 响应数据字典，用于记录实际收到的响应
        """
        self.message = message
        self.response_data = response_data
        super().__init__(self.message)

    def __str__(self):
        """
        返回格式化的错误信息
        
        Returns:
            格式化的错误字符串，包含响应数据（如果有）
        """
        error_msg = f"响应数据无效: {self.message}"
        if self.response_data:
            error_msg += f", 响应数据: {str(self.response_data)[:200]}"
        return error_msg


class ConfigurationError(APIAutomationException):
    """
    配置错误异常
    
    当配置文件缺失、格式错误或配置项无效时抛出此异常。
    
    属性：
        message: 错误消息描述
        config_key: 配置项名称（可选）
    
    使用场景：
        - 配置文件不存在
        - 配置文件格式错误（如YAML语法错误）
        - 必要配置项缺失
        - 配置值无效
    
    示例：
        if not os.path.exists(config_file):
            raise ConfigurationError(
                message="配置文件不存在",
                config_key="http_config.yaml"
            )
    """

    def __init__(self, message: str, config_key: str = None):
        """
        初始化配置错误异常
        
        Args:
            message: 错误消息描述
            config_key: 出错的配置项名称或配置文件路径
        """
        self.message = message
        self.config_key = config_key
        super().__init__(self.message)

    def __str__(self):
        """
        返回格式化的错误信息
        
        Returns:
            格式化的错误字符串，包含配置项名称（如果有）
        """
        error_msg = f"配置错误: {self.message}"
        if self.config_key:
            error_msg += f", 配置项: {self.config_key}"
        return error_msg


class TestDataError(APIAutomationException):
    """
    测试数据错误异常
    
    当测试数据文件缺失、格式错误或数据内容无效时抛出此异常。
    
    属性：
        message: 错误消息描述
        test_case_name: 测试用例名称（可选）
        data_file: 数据文件路径（可选）
    
    使用场景：
        - 测试数据文件不存在
        - YAML数据格式错误
        - 测试数据缺少必要字段
        - 数据值不符合预期
    
    示例：
        test_data = load_yaml("test_data.yaml")
        if "expected_status_code" not in test_data:
            raise TestDataError(
                message="测试数据缺少expected_status_code字段",
                test_case_name="test_login",
                data_file="test_data.yaml"
            )
    """

    def __init__(self, message: str, test_case_name: str = None, data_file: str = None):
        """
        初始化测试数据错误异常
        
        Args:
            message: 错误消息描述
            test_case_name: 出错的测试用例名称
            data_file: 出错的数据文件路径
        """
        self.message = message
        self.test_case_name = test_case_name
        self.data_file = data_file
        super().__init__(self.message)

    def __str__(self):
        """
        返回格式化的错误信息
        
        Returns:
            格式化的错误字符串，包含测试用例名称和数据文件路径（如果有）
        """
        error_msg = f"测试数据错误: {self.message}"
        if self.test_case_name:
            error_msg += f", 测试用例: {self.test_case_name}"
        if self.data_file:
            error_msg += f", 数据文件: {self.data_file}"
        return error_msg


class RetryExhaustedError(APIAutomationException):
    """
    重试耗尽异常
    
    当操作重试次数耗尽后仍失败时抛出此异常。
    
    属性：
        message: 错误消息描述
        max_retries: 最大重试次数
        last_exception: 最后一次异常（可选）
    
    使用场景：
        - HTTP请求重试耗尽
        - 操作多次重试后仍失败
    
    示例：
        raise RetryExhaustedError(
            message="请求重试耗尽",
            max_retries=3,
            last_exception=last_error
        )
    """

    def __init__(self, message: str, max_retries: int = None, last_exception: Exception = None):
        self.message = message
        self.max_retries = max_retries
        self.last_exception = last_exception
        super().__init__(self.message)

    def __str__(self):
        error_msg = f"重试耗尽: {self.message}"
        if self.max_retries:
            error_msg += f", 最大重试次数: {self.max_retries}"
        if self.last_exception:
            error_msg += f", 最后异常: {str(self.last_exception)}"
        return error_msg
