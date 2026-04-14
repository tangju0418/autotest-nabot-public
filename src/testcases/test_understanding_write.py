import pytest
import allure
from src.api.understanding_api import UnderstandingAPI
from src.utils.yaml_loader import get_test_data
from src.utils.error_handler import ExceptionHandler
from src.utils.test_data_helper import prepare_test_data
from src.utils.allure_attach import attach_allure_request_prepare_bundle

WRITE_TEST_DATA = get_test_data("testdata/understanding_write_data.yaml", "test_understanding_write")


def validate_response(resp_json: dict, test_case: dict):
    """校验响应字段"""
    if test_case["expected_status_code"] == 400:
        expected_name = test_case.get("expected_name", "invalid_request")
        expected_data = test_case.get("expected_data")
        assert resp_json.get("name") == expected_name
        assert resp_json.get("data") == expected_data
    elif test_case["expected_status_code"] == 200:
        if "expected_response" in test_case:
            assert resp_json == test_case["expected_response"]
        else:
            resp_data = resp_json if isinstance(resp_json, list) else resp_json.get("data", [])
            assert len(resp_data) > 0
            fact = resp_data[0].get("fact", "")
            assert fact and "expected_fact_contains" not in test_case or \
                test_case["expected_fact_contains"] in fact


@pytest.mark.usefixtures("setup")
@allure.epic("Understanding-write")
class TestUnderstandingWrite:

    @pytest.fixture(autouse=True)
    def setup(self, logger, request):
        self.api = UnderstandingAPI()
        self.logger = logger
        self.request = request

    @pytest.mark.parametrize("test_case", WRITE_TEST_DATA,
                             ids=[tc["name"] for tc in WRITE_TEST_DATA])
    @allure.story("记忆自定义接口")
    @allure.title("{test_case[name]}")
    def test_write(self, test_case):
        allure.dynamic.parameter("test_case", "")
        request_data = prepare_test_data(test_case["data"], prefix="memory_custom")
        expected_status_code = test_case.get("expected_status_code", 200)
        check_status_code = (expected_status_code == 200)
        raw_headers = test_case.get("headers")
        use_env_token = test_case.get("use_env_token", True)
        write_payload = {"data": request_data}

        with allure.step("准备测试数据"):
            self.logger.info(f"开始执行测试用例: {test_case['name']}")
            self.logger.info(f"请求数据: {request_data}")
            self.logger.info(f"请求Headers: {raw_headers}")
            attach_allure_request_prepare_bundle(
                UnderstandingAPI.HTTP_METHOD_WRITE,
                test_case["endpoint"],
                raw_headers,
                json_body=write_payload,
                include_request_body=True,
                use_env_token=use_env_token,
            )

        with ExceptionHandler(self.logger, self.request):
            with allure.step("发送请求"):
                response = self.api.write(
                    endpoint=test_case["endpoint"],
                    data=request_data,
                    headers=raw_headers,
                    check_status_code=check_status_code,
                    use_env_token=use_env_token,
                )
                self._save_response(response, request_data)

            with allure.step("校验响应"):
                assert response.status_code == expected_status_code
                validate_response(response.json(), test_case)

            self.logger.info(f"测试用例执行完成: {test_case['name']}")

    def _save_response(self, response, request_data):
        """保存响应信息"""
        resp_json = response.json()
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.info(f"响应内容: {resp_json}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {resp_json}")
        allure.attach(str(resp_json), "响应内容", attachment_type=allure.attachment_type.JSON)
        self.request.node.last_request_body = str(request_data)
        self.request.node.last_response_body = str(resp_json)
