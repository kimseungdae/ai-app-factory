import os
import yaml
from typing import Dict, Any
from pathlib import Path

class Config:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'settings.yaml')
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_api_key(self, service: str) -> str:
        env_var = f"{service.upper()}_API_KEY"
        api_key = os.getenv(env_var)
        
        if not api_key:
            raise ValueError(f"API key for {service} not found. Please set {env_var} environment variable.")
        
        return api_key
    
    def is_agent_enabled(self, agent_name: str) -> bool:
        return self.get(f'agents.{agent_name}.enabled', False)
    
    @property
    def app_name(self) -> str:
        return self.get('app.name', 'AI App Factory')
    
    @property
    def debug(self) -> bool:
        return self.get('app.debug', False)
    
    @property
    def log_level(self) -> str:
        return self.get('logging.level', 'INFO')
    
    @property
    def log_format(self) -> str:
        return self.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

config = Config()