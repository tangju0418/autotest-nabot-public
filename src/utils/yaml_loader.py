import yaml
from copy import deepcopy
from pathlib import Path

def load_yaml_data(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def _normalize_headers(headers: dict) -> dict:
    return dict(headers)


def _normalize_test_data(value):
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            if key == "headers" and isinstance(item, dict):
                normalized[key] = _normalize_headers(item)
            else:
                normalized[key] = _normalize_test_data(item)
        return normalized

    if isinstance(value, list):
        return [_normalize_test_data(item) for item in value]

    return value


def get_test_data(yaml_file: str, test_case_key: str) -> list:
    data = load_yaml_data(yaml_file)
    return _normalize_test_data(deepcopy(data.get(test_case_key, [])))