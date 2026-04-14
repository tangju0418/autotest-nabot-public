import json
import pytest
import allure
from src.api.focus_api import FocusAPI
from src.utils.yaml_loader import get_test_data
from src.utils.error_handler import ExceptionHandler
from src.utils.allure_attach import attach_allure_request_prepare_bundle

FOCUS_DELETE_TEST_DATA = get_test_data("testdata/focus_delete_data.yaml", "test_focus_delete")


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
        
        return
    except json.JSONDecodeError:
        pass


@pytest.mark.usefixtures("setup")
@allure.epic("Focus-delete")
class TestFocusDelete:

    @pytest.fixture(autouse=True)
    def setup(self, logger, request):
        self.api = FocusAPI()
        self.logger = logger
        self.request = request

    @pytest.mark.parametrize("test_case", FOCUS_DELETE_TEST_DATA,
                             ids=[tc["name"] for tc in FOCUS_DELETE_TEST_DATA])
    @allure.story("删除focus接口")
    @allure.title("{test_case[name]}")
    def test_delete(self, test_case):
        allure.dynamic.parameter("test_case", "")
        raw_headers = test_case.get("headers")
        use_env_token = test_case.get("use_env_token", True)
        
        with allure.step("准备测试数据"):
            self.logger.info(f"开始执行测试用例: {test_case['name']}")
            focus_id = None
            
            if test_case.get("create_focus_first"):
                focus_id = self._create_focus(test_case, use_env_token)
            elif "focus_id" in test_case:
                focus_id = test_case["focus_id"]
            
            self.logger.info(f"Focus ID: {focus_id}")
            self.logger.info(f"请求Headers: {raw_headers}")
            attach_allure_request_prepare_bundle(
                "DELETE",
                f"{test_case['endpoint']}/{focus_id}",
                raw_headers,
                include_request_body=False,
                use_env_token=use_env_token,
            )

        with ExceptionHandler(self.logger, self.request):
            if test_case.get("verify_after_delete"):
                self._test_delete_and_verify(test_case, focus_id)
            elif test_case.get("delete_twice"):
                self._test_delete_twice(test_case, focus_id)
            else:
                self._test_normal_delete(test_case, focus_id)

            self.logger.info(f"测试用例执行完成: {test_case['name']}")

    def _create_focus(self, test_case: dict, use_env_token: bool) -> str:
        """创建focus并返回ID"""
        raw_headers = test_case.get("headers")
        with allure.step("创建focus"):
            create_data = {
                "instruction": "测试删除focus"
            }
            
            self.logger.info("调用create_and_top_level接口创建focus")
            create_response = self.api.create_and_top_level(
                endpoint="/intent-os-mindspace-multi-agent-api/method/api/focus/create_and_top_level",
                data=create_data,
                headers=raw_headers,
                check_status_code=False,
                use_env_token=use_env_token,
            )
            
            self.logger.info(f"创建focus响应状态码: {create_response.status_code}")
            self.logger.info(f"创建focus响应内容: {create_response.text}")
            
            if create_response.status_code in [200, 201]:
                resp_json = json.loads(create_response.text)
                data_list = resp_json.get("data", [])
                if data_list and len(data_list) > 0:
                    focus_id = data_list[0].get("id")
                    self.logger.info(f"成功创建focus，ID: {focus_id}")
                    allure.attach(str(focus_id), "创建的Focus ID", attachment_type=allure.attachment_type.TEXT)
                    return focus_id
            
            pytest.fail(f"创建focus失败，状态码: {create_response.status_code}")

    def _test_normal_delete(self, test_case: dict, focus_id: str):
        """测试正常删除"""
        raw_headers = test_case.get("headers")
        use_env_token = test_case.get("use_env_token", True)
        with allure.step("发送删除请求"):
            response = self.api.delete(
                endpoint=test_case["endpoint"],
                focus_id=focus_id,
                headers=raw_headers,
                check_status_code=False,
                use_env_token=use_env_token,
            )
            self._save_response(response, focus_id)

        with allure.step("校验响应"):
            expected_status_code = test_case.get("expected_status_code", 200)
            assert response.status_code == expected_status_code, \
                f"状态码不匹配，期望: {expected_status_code}，实际: {response.status_code}"
            
            if "expected_response" in test_case:
                validate_response(response.text, test_case)

    def _test_delete_and_verify(self, test_case: dict, focus_id: str):
        """测试删除后验证"""
        raw_headers = test_case.get("headers")
        use_env_token = test_case.get("use_env_token", True)
        with allure.step("第一次删除"):
            response = self.api.delete(
                endpoint=test_case["endpoint"],
                focus_id=focus_id,
                headers=raw_headers,
                check_status_code=False,
                use_env_token=use_env_token,
            )
            self.logger.info(f"第一次删除响应状态码: {response.status_code}")
            
            expected_status_code = test_case.get("expected_status_code", 200)
            assert response.status_code == expected_status_code

        with allure.step("验证删除后查询返回404"):
            verify_response = self.api.hierarchy(
                endpoint=test_case["endpoint"],
                focus_id=focus_id,
                headers=raw_headers,
                check_status_code=False,
                use_env_token=use_env_token,
            )
            self.logger.info(f"删除后查询响应状态码: {verify_response.status_code}")
            self.logger.info(f"删除后查询响应内容: {verify_response.text}")
            
            assert verify_response.status_code == 404, \
                f"删除后应该返回404，实际返回: {verify_response.status_code}"
            
            allure.attach(verify_response.text, "删除后查询响应", attachment_type=allure.attachment_type.TEXT)

    def _test_delete_twice(self, test_case: dict, focus_id: str):
        """测试重复删除（幂等性）"""
        raw_headers = test_case.get("headers")
        use_env_token = test_case.get("use_env_token", True)
        with allure.step("第一次删除"):
            response1 = self.api.delete(
                endpoint=test_case["endpoint"],
                focus_id=focus_id,
                headers=raw_headers,
                check_status_code=False,
                use_env_token=use_env_token,
            )
            self.logger.info(f"第一次删除响应状态码: {response1.status_code}")
            self._save_response(response1, focus_id)
            
            expected_status_code = test_case.get("expected_status_code", 200)
            assert response1.status_code == expected_status_code

        with allure.step("第二次删除（验证幂等性）"):
            response2 = self.api.delete(
                endpoint=test_case["endpoint"],
                focus_id=focus_id,
                headers=raw_headers,
                check_status_code=False,
                use_env_token=use_env_token,
            )
            self.logger.info(f"第二次删除响应状态码: {response2.status_code}")
            self.logger.info(f"第二次删除响应内容: {response2.text}")
            
            assert response2.status_code in [200, 404], \
                f"第二次删除状态码异常: {response2.status_code}"
            
            allure.attach(response2.text, "第二次删除响应", attachment_type=allure.attachment_type.TEXT)

    def _save_response(self, response, focus_id):
        """保存响应信息"""
        resp_text = response.text
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.info(f"响应内容: {resp_text}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {resp_text}")
        allure.attach(resp_text, "响应内容", attachment_type=allure.attachment_type.TEXT)
        self.request.node.last_request_focus_id = str(focus_id)
        self.request.node.last_response_body = resp_text
