from device.pk9019 import PK9019
from pymodbus.exceptions import ModbusException
import time


def test_pk9019():
    try:
        # 创建设备实例
        print("正在连接设备...")
        device = PK9019(host='localhost', port=4197, slave_address=1)  # 使用从机地址1

        # 读取所有通道温度
        print("\n读取所有通道温度")
        temps = device.get_all_temps()
        print(f"原始数据: {temps}")

        # 显示每个通道温度
        for i, temp in enumerate(temps):
            if temp == '断线':
                print(f"通道 {i}: {temp}")
            else:
                print(f"通道 {i}: {temp:.1f}℃")

    except ConnectionError as e:
        print(f"\n连接错误: {e}")
    except ModbusException as e:
        print(f"\n通信错误: {e}")
    except Exception as e:
        print(f"\n其他错误: {e}")


if __name__ == "__main__":
    test_pk9019()