import pytest
import allure
from src.api.ai_phone_planning_api import AIPhonePlanningAPI
from src.utils.yaml_loader import get_test_data
from src.utils.error_handler import ExceptionHandler
from src.utils.allure_attach import attach_allure_request_prepare_bundle

AI_PHONE_PLANNING_TEST_DATA = get_test_data("testdata/ai_phone_planning_find_data.yaml", "test_ai_phone_planning_find")


def validate_response(resp_json: dict, test_case: dict):
    """校验响应字段"""
    if "expected_response" in test_case:
        expected = test_case["expected_response"]
        for key, value in expected.items():
            assert resp_json.get(key) == value, \
                f"字段 '{key}' 校验失败: 预期值={value}, 实际值={resp_json.get(key)}"

    if "expected_fields" in test_case:
        expected = test_case["expected_fields"]
        for key, value in expected.items():
            assert resp_json.get(key) == value, \
                f"字段 '{key}' 校验失败: 预期值={value}, 实际值={resp_json.get(key)}"

    if "expected_nested_fields" in test_case:
        expected_nested = test_case["expected_nested_fields"]
        for field_path, expected_value in expected_nested.items():
            keys = field_path.split(".")
            actual_value = resp_json
            for key in keys:
                actual_value = actual_value.get(key)

            if expected_value == "__NOT_EMPTY__":
                assert actual_value is not None and len(actual_value) > 0, \
                    f"嵌套字段 '{field_path}' 不能为空"
            elif expected_value == "__NOT_NULL__":
                assert actual_value is not None, \
                    f"嵌套字段 '{field_path}' 不能为null"
            else:
                assert actual_value == expected_value, \
                    f"嵌套字段 '{field_path}' 校验失败: 预期值={expected_value}, 实际值={actual_value}"


@pytest.mark.usefixtures("setup")
@allure.epic("AI Phone Planning")
class TestAIPhonePlanningFind:

    @pytest.fixture(autouse=True)
    def setup(self, logger, request):
        self.api = AIPhonePlanningAPI()
        self.logger = logger
        self.request = request

    @pytest.mark.parametrize("test_case", AI_PHONE_PLANNING_TEST_DATA,
                             ids=[tc["name"] for tc in AI_PHONE_PLANNING_TEST_DATA])
    @allure.story("查询planning列表")
    @allure.title("{test_case[name]}")
    def test_find(self, test_case):
        allure.dynamic.parameter("test_case", "")
        expected_status_code = test_case.get("expected_status_code", 200)
        check_status_code = (expected_status_code == 200)
        raw_headers = test_case.get("headers")
        use_env_token = test_case.get("use_env_token", True)

        with allure.step("准备测试数据"):
            self.logger.info(f"开始执行测试用例: {test_case['name']}")
            self.logger.info(f"测试描述: {test_case.get('description', '')}")
            self.logger.info(f"请求Headers: {raw_headers}")
            attach_allure_request_prepare_bundle(
                AIPhonePlanningAPI.HTTP_METHOD_FIND,
                AIPhonePlanningAPI.PATH_FIND,
                raw_headers,
                include_request_body=False,
                use_env_token=use_env_token,
            )

        with ExceptionHandler(self.logger, self.request):
            with allure.step("发送请求"):
                response = self.api.find(
                    headers=raw_headers,
                    check_status_code=check_status_code,
                    use_env_token=use_env_token,
                )
                self._save_response(response)

            with allure.step("校验响应"):
                assert response.status_code == expected_status_code
                validate_response(response.json(), test_case)

            self.logger.info(f"测试用例执行完成: {test_case['name']}")

    def _save_response(self, response):
        """保存响应信息"""
        resp_json = response.json()
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.info(f"响应内容: {resp_json}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {resp_json}")
        allure.attach(str(resp_json), "响应内容", attachment_type=allure.attachment_type.JSON)
        self.request.node.last_response_body = str(resp_json)
