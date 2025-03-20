# PK9019 服务器

这是PK9019设备的服务器程序，用于控制和管理PK9019热电偶温度采集模块。

## 功能特点

- 设备控制和管理
- 环境温度采集
- 8通道温度采集
- 远程操作接口

## 系统要求

- Python 3.7+
- 相关依赖包（见requirements.txt）

## 安装说明

1. 创建虚拟环境（推荐）：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置说明

配置文件位于 `config/config.py`，包含以下配置项：

### Tango服务器配置
```python
tango:
  server_name: "PK9019"      # 服务器名称
  instance_name: "LACT"      # 实例名称
```

### 设备配置
```python
device:
  host: "127.0.0.1"         # PK9019设备IP地址
  port: 4197                # 设备端口号
  slave_address: 1          # 从机地址
```

### 日志配置
```python
logging:
  root:
    level: "INFO"           # 根日志级别
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: "pk9019.log"      # 日志文件路径
  
  modules:
    pymodbus: "INFO"        # pymodbus库的日志级别
    device.pk9019: "INFO"   # PK9019设备模块的日志级别
    server.server_pk9019: "INFO"  # PK9019服务器模块的日志级别
```

## 目录结构

```
PK9019/
├── config/             # 配置文件目录
│   └── config.py      # 配置文件
├── device/            # 设备相关代码
│   └── pk9019.py     # PK9019设备驱动
├── server/            # 服务器代码
│   └── server_pk9019.py  # Tango设备服务器
├── test/             # 测试代码
├── main.py           # 主程序入口
├── requirements.txt  # 依赖包列表
└── README.md        # 项目说明文档
```

## 运行方法

1. 确保配置文件中的设备参数正确

2. 运行服务器：
```bash
python main.py
```

## 设备属性

### 可读属性
- `environment_temp`: 环境温度值（℃）
- `channel_temps`: 8个通道的温度值列表（℃）

### 设备属性
- `host`: PK9019设备IP地址
- `port`: 设备端口号
- `slave_address`: 从机地址

## 日志说明

- 日志同时输出到控制台和文件
- 可通过配置文件调整不同模块的日志级别
- 支持的日志级别：
  - DEBUG：调试信息
  - INFO：一般信息
  - WARNING：警告信息
  - ERROR：错误信息
  - CRITICAL：严重错误信息 