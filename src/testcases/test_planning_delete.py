import json
import pytest
import allure
from src.api.planning_api import PlanningAPI
from src.utils.yaml_loader import get_test_data
from src.utils.error_handler import ExceptionHandler
from src.utils.test_data_helper import prepare_test_data
from src.utils.allure_attach import attach_allure_request_prepare_bundle

DELETE_TEST_DATA = get_test_data("testdata/planning_delete_data.yaml", "test_planning_delete")


def extract_session_id_from_response(resp_text: str) -> str:
    """从conductor响应中提取session_id"""
    lines = resp_text.strip().split('\n')
    for line in lines:
        if line.startswith('data: '):
            try:
                data_str = line[6:]
                resp_json = json.loads(data_str)
                if "session_id" in resp_json:
                    return resp_json["session_id"]
            except json.JSONDecodeError:
                continue
    return None


def validate_response(resp_text: str, test_case: dict):
    """校验响应字段"""
    if "expected_response" not in test_case:
        return
    
    expected = test_case["expected_response"]
    
    try:
        resp_json = json.loads(resp_text)
        for key, value in expected.items():
            assert resp_json.get(key) == value, f"字段 {key} 期望值 {value}，实际值 {resp_json.get(key)}"
        return
    except json.JSONDecodeError:
        pass


@pytest.mark.usefixtures("setup")
@allure.epic("Planning-delete")
class TestPlanningDelete:

    @pytest.fixture(autouse=True)
    def setup(self, logger, request):
        self.api = PlanningAPI()
        self.logger = logger
        self.request = request

    @pytest.mark.parametrize("test_case", DELETE_TEST_DATA,
                             ids=[tc["name"] for tc in DELETE_TEST_DATA])
    @allure.story("删除会话接口")
    @allure.title("{test_case[name]}")
    def test_delete(self, test_case):
        allure.dynamic.parameter("test_case", "")
        raw_headers = test_case.get("headers")
        use_env_token = test_case.get("use_env_token", True)
        
        with allure.step("准备测试数据"):
            self.logger.info(f"开始执行测试用例: {test_case['name']}")
            
            session_id = None
            
            if test_case.get("session_id") is None and "session_id" not in test_case:
                if test_case.get("expected_status_code") == 401:
                    session_id = "dummy_session_id"
                else:
                    conductor_data = {
                        "session_id": "",
                        "focus_id": "auto",
                        "message_id": "",
                        "query": "测试删除会话",
                        "stream": True,
                        "pubsub_topic": ""
                    }
                    conductor_data = prepare_test_data(conductor_data)
                    
                    conductor_headers = raw_headers
                    
                    self.logger.info(f"调用conductor接口创建session")
                    conductor_response = self.api.conductor(
                        endpoint="/planning-api/method/v2/conductor",
                        data=conductor_data,
                        headers=conductor_headers,
                        check_status_code=True,
                        use_env_token=use_env_token,
                    )
                    
                    session_id = extract_session_id_from_response(conductor_response.text)
                    self.logger.info(f"从conductor响应中提取session_id: {session_id}")
                    allure.attach(str(session_id), "Session ID", attachment_type=allure.attachment_type.TEXT)
            
            elif "session_id" in test_case:
                session_id = test_case["session_id"]
            
            self.logger.info(f"请求Headers: {raw_headers}")
            if session_id == "" or session_id is None:
                endpoint_with_params = f"{test_case['endpoint']}?session_id="
            else:
                endpoint_with_params = f"{test_case['endpoint']}?session_id={session_id}"
            attach_allure_request_prepare_bundle(
                "POST",
                endpoint_with_params,
                raw_headers,
                include_request_body=False,
                use_env_token=use_env_token,
            )

        with ExceptionHandler(self.logger, self.request):
            with allure.step("发送删除请求"):
                if session_id == "" or session_id is None:
                    endpoint_with_params = f"{test_case['endpoint']}?session_id="
                else:
                    endpoint_with_params = f"{test_case['endpoint']}?session_id={session_id}"
                
                self.logger.info(f"删除接口endpoint: {endpoint_with_params}")
                
                response = self.api.delete(
                    endpoint=test_case["endpoint"],
                    session_id=session_id if session_id else "",
                    headers=raw_headers,
                    check_status_code=False,
                    use_env_token=use_env_token,
                )
                self._save_response(response)

            with allure.step("校验响应"):
                expected_status_code = test_case.get("expected_status_code", 200)
                assert response.status_code == expected_status_code
                
                if "expected_response" in test_case:
                    validate_response(response.text, test_case)

            self.logger.info(f"测试用例执行完成: {test_case['name']}")

    def _save_response(self, response):
        """保存响应信息"""
        resp_text = response.text
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.info(f"响应内容: {resp_text}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {resp_text}")
        allure.attach(resp_text, "响应内容", attachment_type=allure.attachment_type.TEXT)
        self.request.node.last_response_body = resp_text
