import logging
import sys
from server.server_pk9019 import PK9019Server, run
from config.config import config

def setup_logging():
    """配置日志系统"""
    log_config = config['logging']
    root_config = log_config['root']
    
    # 创建日志格式器
    formatter = logging.Formatter(root_config['format'])
    
    # 创建并配置文件处理器
    file_handler = logging.FileHandler(root_config['file'], encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 创建并配置控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, root_config['level']))
    # 清除现有的处理器
    root_logger.handlers.clear()
    # 添加新的处理器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 配置各个模块的日志级别
    for module, level in log_config['modules'].items():
        module_logger = logging.getLogger(module)
        module_logger.setLevel(getattr(logging, level))

def main():
    # 设置日志
    setup_logging()
    
    # 记录启动信息
    logging.info("PK9019服务启动中...")
    
    # 运行服务器
    try:
        run([PK9019Server], [
            config['tango']['server_name'],
            config['tango']['instance_name']
        ])
    except Exception as e:
        logging.error(f"服务器启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
