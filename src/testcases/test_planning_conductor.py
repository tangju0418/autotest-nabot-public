import pytest
import allure
from src.api.planning_api import PlanningAPI
from src.utils.yaml_loader import get_test_data
from src.utils.error_handler import ExceptionHandler
from src.utils.test_data_helper import prepare_test_data
from src.utils.allure_attach import attach_allure_request_prepare_bundle

CONDUCTOR_TEST_DATA = get_test_data("testdata/planning_conductor_data.yaml", "test_planning_conductor")


def validate_response(resp_text: str, test_case: dict):
    """校验响应字段"""
    if "expected_response" not in test_case:
        return
    
    expected = test_case["expected_response"]
    import json
    
    try:
        resp_json = json.loads(resp_text)
        for key, value in expected.items():
            assert resp_json.get(key) == value, f"字段 {key} 期望值 {value}，实际值 {resp_json.get(key)}"
        return
    except json.JSONDecodeError:
        pass
    
    lines = resp_text.strip().split('\n')
    for line in lines:
        if line.startswith('data: '):
            try:
                data_str = line[6:]
                resp_json = json.loads(data_str)
                
                for key, value in expected.items():
                    assert resp_json.get(key) == value, f"字段 {key} 期望值 {value}，实际值 {resp_json.get(key)}"
                break
            except json.JSONDecodeError:
                continue


@pytest.mark.usefixtures("setup")
@allure.epic("Planning-conductor")
class TestPlanningConductor:

    @pytest.fixture(autouse=True)
    def setup(self, logger, request):
        self.api = PlanningAPI()
        self.logger = logger
        self.request = request

    @pytest.mark.parametrize("test_case", CONDUCTOR_TEST_DATA,
                             ids=[tc["name"] for tc in CONDUCTOR_TEST_DATA])
    @allure.story("规划任务接口")
    @allure.title("{test_case[name]}")
    def test_conductor(self, test_case):
        allure.dynamic.parameter("test_case", "")
        request_data = prepare_test_data(test_case["data"])
        expected_status_code = test_case.get("expected_status_code", 200)
        check_status_code = (expected_status_code == 200)
        raw_headers = test_case.get("headers")
        use_env_token = test_case.get("use_env_token", True)

        with allure.step("准备测试数据"):
            self.logger.info(f"开始执行测试用例: {test_case['name']}")
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
                response = self.api.conductor(
                    endpoint=test_case["endpoint"],
                    data=request_data,
                    headers=raw_headers,
                    check_status_code=check_status_code,
                    use_env_token=use_env_token,
                )
                self._save_response(response, request_data)

            with allure.step("校验响应"):
                assert response.status_code == expected_status_code
                if expected_status_code == 200:
                    validate_response(response.text, test_case)

            self.logger.info(f"测试用例执行完成: {test_case['name']}")

    def _save_response(self, response, request_data):
        """保存响应信息"""
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.info(f"响应内容: {response.text[:500]}...")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}...")
        allure.attach(response.text, "响应内容", attachment_type=allure.attachment_type.TEXT)
        self.request.node.last_request_body = str(request_data)
        self.request.node.last_response_body = response.text
