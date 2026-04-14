"""
环境配置模块

本模块负责管理测试环境配置, 支持:
- 从环境变量读取配置
- 从配置文件读取配置
- 多环境切换(dev/prod/jp, 见 http_config.yaml)

配置优先级:
    API_BASE_URL 环境变量 > 配置文件(按 TEST_ENV) > 默认值

环境变量说明:
    TEST_ENV: 环境名称, 默认 dev
    API_BASE_URL: 覆盖配置文件中的 base_url
    API_TOKEN: 通用 API 认证 Token
    API_TOKEN_<ENV大写>: 环境专属 token, 如 API_TOKEN_DEV
    DEBUG: 调试模式(true/false)
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from src.utils.config_loader import config_loader, get_environment_config

_DOTENV_LOADED = False


def _normalize_env_text(value: Optional[str]) -> str:
    """清洗环境变量中的首尾空白, 避免 secret 末尾换行污染请求头."""
    return value.strip() if isinstance(value, str) else ""


def project_root() -> Path:
    """autotest-nabot 仓库根目录(含 pyproject.toml、.env)."""
    return Path(__file__).resolve().parents[2]


def load_project_dotenv() -> None:
    """将项目根 .env 读入 os.environ; 已存在的环境变量不被覆盖."""
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return

    env_path = project_root() / ".env"
    if not env_path.is_file():
        _DOTENV_LOADED = True
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val

    _DOTENV_LOADED = True


load_project_dotenv()


class EnvConfig:
    """环境配置(单例 env_config)."""

    def __init__(self) -> None:
        self._env_config_key: Optional[str] = None
        self._env_config_dict: Optional[Dict[str, Any]] = None

    def _current_env_dict(self) -> Dict[str, Any]:
        env_name = os.getenv("TEST_ENV", "dev")
        if self._env_config_dict is None or self._env_config_key != env_name:
            self._env_config_key = env_name
            self._env_config_dict = get_environment_config(env_name)
        return self._env_config_dict

    @property
    def ENV(self) -> str:
        return os.getenv("TEST_ENV", "dev")

    @property
    def TOKEN(self) -> str:
        return self.token_for_env()

    def token_for_env(self, env_name: Optional[str] = None) -> str:
        """按环境读取默认 token, 优先环境专属变量, 再回退到 API_TOKEN."""
        effective_env = (env_name or self.ENV).upper()
        env_token = _normalize_env_text(os.getenv(f"API_TOKEN_{effective_env}"))
        if env_token:
            return env_token
        return _normalize_env_text(os.getenv("API_TOKEN", ""))

    @property
    def DEBUG(self) -> bool:
        return os.getenv("DEBUG", "false").lower() == "true"

    @property
    def BASE_URL(self) -> str:
        env_url = os.getenv("API_BASE_URL")
        if env_url:
            return env_url
        return self._current_env_dict().get(
            "base_url", "https://api.dev.brain.ai/v1.0/invoke"
        )

    @property
    def TIMEOUT(self) -> float:
        d = self._current_env_dict()
        if d.get("timeout") is not None:
            return float(d["timeout"])
        return float(config_loader.get_http_config().get("timeout", 30))

    @property
    def VERIFY_SSL(self) -> bool:
        d = self._current_env_dict()
        if "verify_ssl" in d:
            return bool(d["verify_ssl"])
        return bool(config_loader.get_http_config().get("verify_ssl", False))


env_config = EnvConfig()
