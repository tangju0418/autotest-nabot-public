# BrainAutoTest

企业级API自动化测试框架，基于 pytest + requests 构建，提供完整的测试解决方案。

当前 public 仓库仅保留 `/userly/method/users/me.json` 的获取测试，用于演示环境配置、接口封装、数据驱动和报告生成链路。

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 **统一异常处理** | 上下文管理器统一处理5种异常类型，自动记录日志和Allure报告 |
| 🔄 **智能重试机制** | 失败自动重试装饰器，支持自定义重试次数和延迟 |
| 📊 **多维度报告** | 同时生成Allure和HTML报告，支持请求/响应详情展示 |
| 📝 **日志追踪** | 完整的日志记录系统，支持按时间戳分文件存储 |
| 🏷️ **数据驱动** | YAML文件管理测试数据，支持参数化测试 |
| 🛡️ **HTTP封装** | 统一的HTTP客户端，支持重试、超时、SSL验证配置 |
| 🎨 **装饰器模式** | 提供多种实用装饰器：错误处理、重试、跳过、步骤记录 |
| 👤 **单接口示例** | 当前仓库聚焦 `me.json` 当前用户接口，便于公开演示与维护 |
| ⚡ **极速包管理** | 使用 uv 工具进行高效的 Python 环境和依赖管理 |

## 📦 技术栈

| 组件 | 版本 | 用途 |
|------|------|------|
| pytest | 9.0.2 | 测试框架 |
| requests | 2.32.3 | HTTP客户端 |
| allure-pytest | 2.15.3 | Allure报告 |
| pytest-html | 4.2.0 | HTML报告 |
| PyYAML | 6.0.2 | 数据管理 |
| urllib3 | 2.3.0 | HTTP连接池 |
| uv | latest | Python环境管理 |

## 📁 目录结构

```
brainautotest/
├── src/                        # 源代码目录
│   ├── config/                 # 配置层
│   ├── api/                    # 接口调用层
│   ├── utils/                  # 公共工具层
│   └── testcases/              # 测试用例层
├── testdata/                   # 测试数据层（当前仅保留 user_profile_data.yaml）
├── bucket/                     # 输出目录
│   ├── logs/                   # 日志文件
│   ├── allure-results/         # Allure 原始数据
│   ├── allure-report/          # Allure HTML 报告
│   ├── history/                # 历史记录
│   ├── archives/               # 归档报告（按时间存储）
│   └── html-report/            # HTML 报告
├── .github/                    # GitHub Actions 配置
├── .gitignore                  # Git 忽略配置
├── conftest.py                 # pytest 配置和钩子函数
├── run.py                      # 执行入口
├── pyproject.toml              # uv 项目配置
└── README.md                   # 项目文档
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.12+
- uv 包管理工具

### 2. 安装 uv（如果未安装）

```bash
pip install uv
```

### 3. 使用 uv 管理项目

```bash
# 安装指定 Python 版本
uv python install 3.12

# 创建虚拟环境
uv venv .venv --python=3.12

# 同步安装依赖（根据 pyproject.toml）
uv sync
```

### 4. 安装 Allure CLI（可选，用于生成 Allure 报告）

```bash
# Windows (使用scoop)
scoop install allure

# Mac (使用Homebrew)
brew install allure

# Linux (使用apt)
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update
sudo apt-get install allure
```

### 5. 配置环境变量

```bash
# Windows
set API_TOKEN=your_token_here
set API_BASE_URL=https://api.example.com/v1

# Linux/Mac
export API_TOKEN=your_token_here
export API_BASE_URL=https://api.example.com/v1
```

### 6. 运行测试

```bash
# 方式一：使用 Python 脚本（推荐，自动生成报告）
python run.py

# 方式二：直接使用 pytest
pytest src/testcases/ -v

# 方式三：运行指定文件
pytest src/testcases/test_user_profile.py -v

# 方式四：按用例名称筛选
pytest src/testcases/test_user_profile.py -v -k "基本信息"
```

## 🎯 核心功能详解

### 1. 统一异常处理

使用 `ExceptionHandler` 上下文管理器统一处理测试异常：

```python
from src.utils.error_handler import ExceptionHandler

def test_api_call(self):
    with ExceptionHandler(self.logger, self.request):
        response = self.api.get("/users")
        assert response.status_code == 200
```

**处理的异常类型：**
- `ConnectionError` / `TimeoutError`: 网络异常
- `RetryExhaustedError`: 重试耗尽
- `InvalidResponseError`: 响应数据无效
- `APIAutomationException`: API异常
- `AssertionError`: 断言失败
- `Exception`: 未预期异常

### 2. 当前保留测试范围

当前 public 仓库只保留一个测试文件和一份测试数据:

```text
src/testcases/test_user_profile.py
testdata/user_profile_data.yaml
```

**支持的校验方式：**
- `expected_response`: 完全匹配响应内容
- `expected_fields`: 校验顶层字段
- `expected_nested_fields`: 校验嵌套字段

### 3. 测试数据 YAML 字段说明

```yaml
test_user_profile:
  - name: "校验用户基本信息"            # 测试用例名称
    description: "验证获取当前用户信息接口返回正确的数据"
    use_env_token: true                # 是否使用环境变量中的 token
    expected_status_code: 200          # 预期状态码
    expected_fields:                   # 顶层字段断言
      email: "tangju+002@brain.im"
```

### 4. 错误处理装饰器

#### @handle_api_errors - API错误处理
```python
from src.utils.error_handler import handle_api_errors

@handle_api_errors
def get_user(user_id):
    response = http_client.get(f"/api/users/{user_id}")
    return response.json()
```

#### @retry_on_failure - 失败重试
```python
from src.utils.error_handler import retry_on_failure

@retry_on_failure(max_retries=3, delay=1.0)
def test_unstable_api():
    response = http_client.get("/api/unstable")
    assert response.status_code == 200
```

#### @skip_on_error - 错误跳过
```python
from src.utils.error_handler import skip_on_error
from src.utils.exceptions import ConnectionError

@skip_on_error(error_type=ConnectionError, reason="网络不可用")
def test_external_api():
    response = http_client.get("https://external-api.com/data")
    assert response.status_code == 200
```

### 5. 自定义异常体系

框架提供7种自定义异常类：

| 异常类 | 说明 | 使用场景 |
|--------|------|----------|
| `APIAutomationException` | 基础异常类 | 通用API异常 |
| `HTTPRequestError` | HTTP请求异常 | 状态码4xx/5xx |
| `ConnectionError` | 网络连接异常 | 网络不可达、DNS失败 |
| `TimeoutError` | 请求超时异常 | 请求/响应超时 |
| `RetryExhaustedError` | 重试耗尽异常 | 多次重试后仍失败 |
| `InvalidResponseError` | 响应无效异常 | 响应格式错误、缺少字段 |
| `ConfigurationError` | 配置错误异常 | 配置文件缺失/格式错误 |
| `TestDataError` | 测试数据错误异常 | 测试数据缺失/无效 |

### 6. HTTP客户端配置

在 `config/http_config.yaml` 中配置HTTP客户端：

```yaml
timeout: 30
max_retries: 3
retry_delay: 1.0
verify_ssl: false
```

### 7. pytest 钩子函数

框架提供自定义 pytest 钩子函数：

```python
# conftest.py 中的钩子函数

# 测试用例收集完成后修改名称（支持中文显示）
def pytest_collection_modifyitems(items):
    for item in items:
        print(f"\n收集测试用例: {item.name}")
        print(f"节点ID: {item.nodeid}")

# 测试报告生成钩子（添加请求/响应信息）
def pytest_runtest_makereport(item, call):
    # 将请求体和响应体附加到报告
    if hasattr(item, "last_request_body"):
        report.req_body = item.last_request_body
    if hasattr(item, "last_response_body"):
        report.resp_body = item.last_response_body
    if hasattr(item, "last_test_title"):
        report.test_title = item.last_test_title

# 自定义 HTML 报告表格（添加测试标题、请求体、响应体列）
def pytest_html_results_table_header(cells):
    cells.insert(2, '<th>测试标题</th>')
    cells.insert(3, '<th>请求体</th>')
    cells.insert(4, '<th>响应体</th>')
```

## 📊 测试报告

运行后自动生成多种格式的报告：

| 报告类型 | 路径 | 说明 |
|----------|------|------|
| HTML报告 | `bucket/html-report/report.html` | 包含请求/响应详情 |
| Allure数据 | `bucket/allure-results/` | Allure原始数据 |
| Allure HTML | `bucket/allure-report/index.html` | Allure可视化报告 |
| 归档报告 | `bucket/archives/YYYYMMDD_HHMMSS/` | 每次执行的报告副本 |
| 日志文件 | `bucket/logs/test_*.log` | 完整的执行日志 |

### 查看 Allure 报告

```bash
# 方式一：启动本地服务（实时更新）
allure serve bucket/allure-results

# 方式二：直接打开HTML文件
open bucket/allure-report/index.html  # Mac
start bucket/allure-report/index.html  # Windows
```

## 🔧 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| API_BASE_URL | API基础地址 | https://plan-dev.api.brain.ai/v1.0 |
| API_TOKEN | 认证Token | （空） |
| TEST_ENV | 测试环境 | dev |
| DEBUG | 调试模式 | false |

## 📝 最佳实践

### 1. 测试用例编写规范

```python
import pytest
import allure
from src.utils.error_handler import ExceptionHandler
from src.api.user_api import UserAPI
from src.utils.yaml_loader import get_test_data

USER_PROFILE_TEST_DATA = get_test_data("testdata/user_profile_data.yaml", "test_user_profile")

class TestUserProfile:
    @pytest.fixture(autouse=True)
    def setup(self, logger, request):
        self.api = UserAPI()
        self.logger = logger
        self.request = request

    @pytest.mark.parametrize("test_case", USER_PROFILE_TEST_DATA,
                         ids=[tc["name"] for tc in USER_PROFILE_TEST_DATA])
    @allure.story("获取当前用户信息")
    @allure.title("{test_case[name]}")
    def test_user_profile(self, test_case):
        with ExceptionHandler(self.logger, self.request):
            response = self.api.get_current_user(
                headers=test_case.get("headers"),
                check_status_code=(test_case.get("expected_status_code", 200) == 200),
                use_env_token=test_case.get("use_env_token", True),
            )
            assert response.status_code == test_case["expected_status_code"]
```

### 2. 测试数据管理

当前测试数据集中在 `testdata/user_profile_data.yaml`：

```yaml
test_user_profile:
  - name: "校验用户基本信息"
    description: "验证获取当前用户信息接口返回正确的数据"
    use_env_token: true
    expected_status_code: 200
    expected_fields:
      email: "tangju+002@brain.im"
```

## 🛠️ 维护约定

### 用例更新职责
- **接口用例**：当前仅维护 `user_profile_data.yaml` 中的当前用户接口测试数据
- **框架变更**：由测试开发维护 `api/` 和 `utils/` 公共模块

### 接口契约变更流程
1. 接口文档更新后，通知测试负责人
2. 测试负责人更新 `testdata/user_profile_data.yaml`
3. 如有新字段或废弃字段，同步更新 `api/*.py` 封装
4. 运行当前用户接口测试验证兼容性

## 🐛 故障排查

### 1. 查看日志文件
```bash
# 查看最新日志
tail -f bucket/logs/test_*.log

# Windows
type bucket\logs\test_*.log
```

### 2. 常见问题

**Q: Allure报告无法生成？**
A: 确保已安装Allure CLI并添加到PATH环境变量

**Q: 测试失败但看不到详细错误？**
A: 检查 `logs/` 目录下的日志文件，包含完整的请求/响应信息

**Q: 如何调试单个测试用例？**
A: 运行 `pytest src/testcases/test_user_profile.py -v`，或使用 `-k` 参数筛选具体用例名

**Q: uv 同步依赖失败？**
A: 确保 pyproject.toml 中 dependencies 字段格式正确，Python 版本符合 requires-python 要求

## 📈 性能指标

- **测试执行时间**: 取决于当前用户接口响应时间，当前默认仅 1 个用例
- **并发支持**: 支持pytest-xdist并行执行
- **内存占用**: < 100MB
- **日志文件**: 自动按日期分割，避免单个文件过大

## 🤝 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目仅供内部使用，未经授权不得外传。

## 📞 联系方式

如有问题，请联系测试开发团队。
