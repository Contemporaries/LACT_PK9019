from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification


def run_modbus_server(host="localhost", port=502):
    """
    启动 Modbus TCP 服务端
    :param host: 服务端 IP 地址（默认 localhost）
    :param port: 服务端端口（默认 502）
    """
    # 初始化数据存储
    # 保持寄存器（地址 0-99，初始值为 0）
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [0] * 100)  # 保持寄存器
    )

    # 创建 Modbus 上下文
    context = ModbusServerContext(slaves=store, single=True)

    # 设置设备标识信息
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'https://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Modbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    # 启动 Modbus TCP 服务端
    print(f"启动 Modbus TCP 服务端，监听 {host}:{port}...")
    StartTcpServer(
        context=context,
        identity=identity,
        address=(host, port)
    )


if __name__ == "__main__":
    # 配置参数
    host = "10.2.101.14"  # 服务端 IP 地址
    port = 4198          # 服务端端口

    # 启动 Modbus TCP 服务端
    run_modbus_server(host, port)