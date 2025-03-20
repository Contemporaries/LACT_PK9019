import yaml
import sys

def load_config(config_file='configuration.yml'):
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        sys.exit(1)

config = load_config()