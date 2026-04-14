import uuid
import random
from datetime import datetime, timezone
from typing import Union, Dict, List


def prepare_test_data(data: Union[Dict, List], prefix: str = None) -> Union[Dict, List]:
    """
    动态生成测试数据，支持 dict 和 list 类型
    
    Args:
        data: 测试数据，可以是字典或列表
        prefix: scenario_id 的前缀，如果为 None 则不生成新的 scenario_id
    
    Returns:
        处理后的测试数据，类型与输入一致
    """
    if isinstance(data, dict):
        return _prepare_single_item(data, prefix)
    elif isinstance(data, list):
        return [_prepare_single_item(item, prefix) for item in data]
    else:
        raise TypeError(f"不支持的测试数据类型: {type(data)}，仅支持 dict 或 list")


def _prepare_single_item(item: Dict, prefix: str = None) -> Dict:
    """
    处理单个测试数据项
    
    Args:
        item: 单个测试数据字典
        prefix: scenario_id 的前缀
    
    Returns:
        处理后的测试数据字典
    """
    item = item.copy()
    
    if prefix and "scenario_id" in item:
        item["scenario_id"] = f"{prefix}_{uuid.uuid4().hex}"
    
    if "timestamp" in item and item["timestamp"] != "":
        item["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    if "message_id" in item:
        timestamp_ms = int(datetime.now().timestamp() * 1000)
        random_suffix = random.randint(100, 999)
        item["message_id"] = f"{timestamp_ms}{random_suffix}"
    
    if "session_id" in item:
        item["session_id"] = str(uuid.uuid4())
    
    if "pubsub_topic" in item:
        item["pubsub_topic"] = str(uuid.uuid4())
    
    return item
