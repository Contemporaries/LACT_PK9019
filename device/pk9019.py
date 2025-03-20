import logging
import struct
from typing import List

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# 配置日志
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG
)

# 设置pymodbus的日志级别为DEBUG
logging.getLogger('pymodbus').setLevel(logging.DEBUG)

log = logging.getLogger()


def calculate_crc(data: bytes) -> bytes:
    """
    计算CRC校验码

    Args:
        data: 需要计算CRC的数据

    Returns:
        bytes: 2字节的CRC校验码
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)


class PK9019:
    """PK9019热电偶温度采集模块类"""

    def __init__(self, host: str, port: int = 502, slave_address: int = 1):
        """
        初始化PK9019设备

        Args:
            host: 设备IP地址
            port: 设备端口号，默认502
            slave_address: 从机地址，默认为1
        """
        self.host = host
        self.port = port
        self.slave_address = slave_address

        log.info(f"正在连接设备 {host}:{port}, 从机地址: {slave_address}")

        # 创建TCP客户端
        self.client = ModbusTcpClient(
            host=self.host,
            port=self.port,
            timeout=10,  # 超时时间10秒
            retries=3,  # 重试3次
        )

        # 尝试连接
        if not self.client.connect():
            raise ConnectionError(f"无法连接到设备: {self.host}:{self.port}")
        log.info("设备连接成功")

    def get_environment_temp(self) -> float:
        """
        获取环境温度
        按照文档示例：
        - 从机地址: 01
        - 功能码: 03 (读取寄存器)
        - 起始地址: 00 01 (0x0001)
        - 读取点数: 00 01 (1个寄存器)

        Returns:
            float: 环境温度值，单位℃
        """
        try:
            # 构建RTU请求帧
            request = struct.pack('>BBHH',
                                  self.slave_address,  # 从机地址
                                  0x03,  # 功能码(读保持寄存器)
                                  0x0001,  # 起始地址
                                  0x0001  # 寄存器数量
                                  )

            # 添加CRC校验
            request += calculate_crc(request)

            log.debug(f"发送请求: {request.hex()}")
            self.client.socket.send(request)

            # 接收响应
            response = self.client.socket.recv(1024)
            log.debug(f"收到响应: {response.hex()}")

            if len(response) < 5:  # 最小响应长度
                raise ModbusException("响应数据长度不足")

            # 解析响应
            # 从机地址(1字节) + 功能码(1字节) + 字节数(1字节) + 数据(2字节) + CRC(2字节)
            slave_addr, func_code = struct.unpack('>BB', response[:2])

            # 检查错误响应
            if func_code & 0x80:  # 最高位为1表示错误响应
                error_code = response[2]
                error_msg = {
                    0x01: "非法功能",
                    0x02: "非法数据地址",
                    0x03: "非法数据值",
                    0x04: "从机设备故障",
                    0x05: "确认",
                    0x06: "从机设备忙",
                    0x08: "存储奇偶性差错",
                    0x0A: "不可用网关路径",
                    0x0B: "网关目标设备无响应"
                }.get(error_code, "未知错误")
                raise ModbusException(f"设备返回错误: {error_msg}")

            # 正常响应解析
            byte_count = response[2]
            data = struct.unpack('>H', response[3:5])

            # return data[0] / 10.0
            # Env temp not divided by 10
            return data[0]

        except Exception as e:
            log.error(f"读取环境温度失败: {str(e)}")
            raise ModbusException(f"读取环境温度失败: {str(e)}")

    def get_all_temps(self) -> List[float]:
        """
        获取所有通道的温度值
        按照文档示例：
        - 从机地址: 01
        - 功能码: 03 (读取寄存器)
        - 起始地址: 00 02 (0x0002)
        - 读取点数: 00 08 (8个寄存器)

        Returns:
            List[float]: 8个通道的温度值列表，单位℃
        """
        try:
            # 构建RTU请求帧
            request = struct.pack('>BBHH',
                                  self.slave_address,  # 从机地址
                                  0x03,  # 功能码(读保持寄存器)
                                  0x0002,  # 起始地址
                                  0x0008  # 寄存器数量
                                  )

            # 添加CRC校验
            request += calculate_crc(request)

            log.debug(f"发送请求: {request.hex()}")
            self.client.socket.send(request)

            # 接收响应
            response = self.client.socket.recv(1024)
            log.debug(f"收到响应: {response.hex()}")

            if len(response) < 5:  # 最小响应长度
                raise ModbusException("响应数据长度不足")

            # 解析响应
            # 从机地址(1字节) + 功能码(1字节) + 字节数(1字节) + 数据(2*8字节) + CRC(2字节)
            slave_addr, func_code = struct.unpack('>BB', response[:2])

            # 检查错误响应
            if func_code & 0x80:  # 最高位为1表示错误响应
                error_code = response[2]
                error_msg = {
                    0x01: "非法功能",
                    0x02: "非法数据地址",
                    0x03: "非法数据值",
                    0x04: "从机设备故障",
                    0x05: "确认",
                    0x06: "从机设备忙",
                    0x08: "存储奇偶性差错",
                    0x0A: "不可用网关路径",
                    0x0B: "网关目标设备无响应"
                }.get(error_code, "未知错误")
                raise ModbusException(f"设备返回错误: {error_msg}")

            # 正常响应解析
            byte_count = response[2]
            data = struct.unpack('>HHHHHHHH', response[3:19])

            temps = []
            for i, reg in enumerate(data):
                if reg == 0x5555:  # 断线值
                    temps.append('断线')
                    log.debug(f"通道{i}断线")
                else:
                    temp = reg / 10.0
                    temps.append(temp)
                    log.debug(f"通道{i}温度: {temp:.1f}℃")

            return temps

        except Exception as e:
            log.error(f"读取温度数据失败: {str(e)}")
            raise ModbusException(f"读取温度数据失败: {str(e)}")

    def __del__(self):
        """析构函数，确保关闭连接"""
        try:
            if self.client:
                self.client.close()
                log.info("关闭设备连接")
        except:
            pass
