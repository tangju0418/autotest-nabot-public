import json
import pytest
import allure
from src.api.focus_api import FocusAPI
from src.utils.yaml_loader import get_test_data
from src.utils.error_handler import ExceptionHandler
from src.utils.allure_attach import attach_allure_request_prepare_bundle

FOCUS_TEST_DATA = get_test_data("testdata/focus_create_and_top_level_data.yaml", "test_focus_create_and_top_level")


def validate_response(resp_text: str, test_case: dict):
    """校验响应字段"""
    if "expected_response" not in test_case:
        return
    
    expected = test_case["expected_response"]
    
    try:
        resp_json = json.loads(resp_text)
        
        for key, value in expected.items():
            if isinstance(value, dict):
                resp_value = resp_json.get(key, {})
                for sub_key, sub_value in value.items():
                    assert resp_value.get(sub_key) == sub_value, \
                        f"字段 {key}.{sub_key} 期望值 {sub_value}，实际值 {resp_value.get(sub_key)}"
            else:
                assert resp_json.get(key) == value, f"字段 {key} 期望值 {value}，实际值 {resp_json.get(key)}"
        
        if "expected_title_contains" in test_case:
            data_list = resp_json.get("data", [])
            if data_list and len(data_list) > 0:
                title = data_list[0].get("title", "")
                expected_keyword = test_case["expected_title_contains"]
                assert expected_keyword in title, f"title字段 '{title}' 不包含 '{expected_keyword}'"
        
        return
    except json.JSONDecodeError:
        pass


@pytest.mark.usefixtures("setup")
@allure.epic("Focus-create_and_top_level")
class TestFocusCreateAndTopLevel:

    @pytest.fixture(autouse=True)
    def setup(self, logger, request):
        self.api = FocusAPI()
        self.logger = logger
        self.request = request

    @pytest.mark.parametrize("test_case", FOCUS_TEST_DATA,
                             ids=[tc["name"] for tc in FOCUS_TEST_DATA])
    @allure.story("创建并获取顶级focus接口")
    @allure.title("{test_case[name]}")
    def test_create_and_top_level(self, test_case):
        allure.dynamic.parameter("test_case", "")
        raw_headers = test_case.get("headers")
        use_env_token = test_case.get("use_env_token", True)
        
        with allure.step("准备测试数据"):
            self.logger.info(f"开始执行测试用例: {test_case['name']}")
            request_data = test_case.get("data", {})
            self.logger.info(f"请求数据: {request_data}")
            self.logger.info(f"请求Headers: {raw_headers}")
            attach_allure_request_prepare_bundle(
                "POST",
                test_case["endpoint"],
                raw_headers,
                json_body=request_data,
                include_request_body=True,
                use_env_token=use_env_token,
            )

        with ExceptionHandler(self.logger, self.request):
            with allure.step("发送请求"):
                response = self.api.create_and_top_level(
                    endpoint=test_case["endpoint"],
                    data=request_data,
                    headers=raw_headers,
                    check_status_code=False,
                    use_env_token=use_env_token,
                )
                self._save_response(response, request_data)

            with allure.step("校验响应"):
                expected_status_code = test_case.get("expected_status_code", 200)
                assert response.status_code == expected_status_code
                
                if "expected_response" in test_case:
                    validate_response(response.text, test_case)

            self.logger.info(f"测试用例执行完成: {test_case['name']}")

    def _save_response(self, response, request_data):
        """保存响应信息"""
        resp_text = response.text
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.info(f"响应内容: {resp_text}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {resp_text}")
        allure.attach(resp_text, "响应内容", attachment_type=allure.attachment_type.TEXT)
        self.request.node.last_request_body = str(request_data)
        self.request.node.last_response_body = resp_text
