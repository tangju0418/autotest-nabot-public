import src.config.env_config  # noqa: F401 加载项目根 .env

import pytest
from src.config.env_config import env_config
from src.utils.logger import get_logger


def pytest_sessionstart(session):
    log = get_logger("api_test")
    log.info(
        f"[EnvConfig] pytest_sessionstart | TEST_ENV={env_config.ENV} | "
        f"BASE_URL={env_config.BASE_URL}"
    )


@pytest.fixture(scope="session")
def logger():
    """
    Session级别的日志fixture
    返回一个配置好的logger实例，用于在测试过程中记录日志
    """
    return get_logger("api_test")


def pytest_configure(config):
    """
    pytest初始化配置
    注册自定义标记，用于标记测试用例类型
    """
    config.addinivalue_line(
        "markers", "req_body: mark test with request body"
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试报告生成钩子
    在测试执行完成后，将请求体和响应体附加到测试报告对象上
    便于后续在HTML报告中展示
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        if hasattr(item, "last_request_body"):
            report.req_body = item.last_request_body
        if hasattr(item, "last_response_body"):
            report.resp_body = item.last_response_body


def pytest_collection_modifyitems(items):
    """
    钩子函数
    测试用例收集完成时将item的name、nodeid转为中文编码显示在控制台
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")


@pytest.hookimpl(tryfirst=True)
def pytest_html_report_title(report):
    """
    设置HTML报告的标题
    """
    report.title = "API自动化测试报告"


def pytest_html_results_table_header(cells):
    """
    自定义HTML报告表格表头
    在标准列后插入"请求体"和"响应体"两列
    """
    cells.insert(2, '<th class="sortable" data-column-type="text">请求体</th>')
    cells.insert(3, '<th class="sortable" data-column-type="text">响应体</th>')


def pytest_html_results_table_row(report, cells):
    """
    自定义HTML报告表格数据行
    读取报告中附加的req_body和resp_body数据
    如果没有则显示"-"
    """
    req_body = getattr(report, 'req_body', '-')
    resp_body = getattr(report, 'resp_body', '-')
    cells.insert(2, f'<td>{req_body}</td>')
    cells.insert(3, f'<td>{resp_body}</td>')