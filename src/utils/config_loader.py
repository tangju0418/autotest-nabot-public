import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from src.utils.exceptions import ConfigurationError
from src.utils.logger import get_logger

logger = get_logger("config_loader")


class ConfigLoader:
    """配置文件加载器"""
    
    _instance = None
    _config_cache: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_yaml_config(self, config_file: str) -> Dict[str, Any]:
        """
        加载YAML配置文件
        
        Args:
            config_file: 配置文件路径（相对于项目根目录）
        
        Returns:
            配置字典
        
        Raises:
            ConfigurationError: 配置文件不存在或格式错误
        """
        if config_file in self._config_cache:
            return self._config_cache[config_file]
        
        config_path = Path(__file__).parent.parent / config_file
        
        if not config_path.exists():
            logger.error(f"配置文件不存在: {config_path}")
            raise ConfigurationError(
                message=f"配置文件不存在: {config_file}",
                config_key=config_file
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self._config_cache[config_file] = config
                logger.info(f"成功加载配置文件: {config_file}")
                return config
        except yaml.YAMLError as e:
            logger.error(f"配置文件格式错误: {config_file}, 错误: {str(e)}")
            raise ConfigurationError(
                message=f"配置文件格式错误: {str(e)}",
                config_key=config_file
            )
        except Exception as e:
            logger.error(f"加载配置文件失败: {config_file}, 错误: {str(e)}")
            raise ConfigurationError(
                message=f"加载配置文件失败: {str(e)}",
                config_key=config_file
            )
    
    def get_http_config(self) -> Dict[str, Any]:
        """
        获取HTTP配置
        
        Returns:
            HTTP配置字典
        """
        config = self.load_yaml_config("config/http_config.yaml")
        return config.get("http", {})
    
    def get_environment_config(self, env: str = None) -> Dict[str, Any]:
        """
        获取环境配置
        
        Args:
            env: 环境名称（dev/test/staging/prod），如果为None则从环境变量读取
        
        Returns:
            环境配置字典
        """
        import os
        
        if env is None:
            env = os.getenv("TEST_ENV", "dev")
        
        config = self.load_yaml_config("config/http_config.yaml")
        environments = config.get("environments", {})
        
        if env not in environments:
            logger.warning(f"环境配置不存在: {env}, 使用默认环境: dev")
            env = "dev"
        
        return environments.get(env, environments.get("dev", {}))
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        获取日志配置
        
        Returns:
            日志配置字典
        """
        config = self.load_yaml_config("config/http_config.yaml")
        return config.get("logging", {})
    
    def clear_cache(self):
        """清除配置缓存"""
        self._config_cache.clear()
        logger.info("配置缓存已清除")


config_loader = ConfigLoader()


def get_http_timeout() -> float:
    """获取HTTP超时时间"""
    http_config = config_loader.get_http_config()
    return http_config.get("timeout", 30.0)


def get_environment_config(env: str = None) -> Dict[str, Any]:
    """获取环境配置"""
    from src.config.env_config import load_project_dotenv

    load_project_dotenv()
    return config_loader.get_environment_config(env)
