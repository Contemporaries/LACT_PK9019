import logging
from tango import DevShort, DevState, DevFloat, AttrWriteType
from tango.server import Device, attribute, run, device_property
from device.pk9019 import PK9019
from device.temp_humidity import TempHumidity
from config.config import config
log = logging.getLogger(__name__)



class PK9019Server(Device):
    """PK9019热电偶温度采集模块Tango设备服务器"""
    pk9019_device = None
    temp_humidity_device = None
    
    # 定义属性
    temp_humidity_host = device_property(
        dtype="str",
        default_value=config['device']['temp_humidity_host'],
        doc="温度湿度采集模块IP地址"
    )   
    
    temp_humidity_port = device_property(
        dtype="int",
        default_value=config['device']['temp_humidity_port'],
        doc="温度湿度采集模块端口号"
    )   
    
    temp_humidity_slave_address = device_property(
        dtype=DevShort,
        default_value=config['device']['temp_humidity_slave_address'],
        doc="温度湿度采集模块从机地址"
    )   
    
    
    host = device_property(
        dtype="str",
        default_value=config['device']['host'],
        doc="PK9019 IP Address"
    )

    port = device_property(
        dtype="int",
        default_value=config['device']['port'],
        doc="PORT Address"
    )

    slave_address = device_property(
        dtype=DevShort,
        default_value=config['device']['slave_address'],
        doc="Slave Address"
    )
    
    temp_humidity: tuple[float] = attribute(
        name="temp_humidity",
        label="温度湿度",
        dtype=(float,),
        max_dim_x=2,
        access=AttrWriteType.READ,
        doc="温度湿度值，单位℃",
        fget="read_temp_humidity"
    )

    environment_temp = attribute(
        name="environment_temp",
        label="环境温度",
        dtype=DevFloat,
        access=AttrWriteType.READ,
        doc="环境温度值，单位℃",
        fget="read_environment_temp"
    )

    channel_temps: tuple[float] = attribute(
        name="channel_temps",
        label="通道温度",
        dtype=(float,),
        access=AttrWriteType.READ,
        max_dim_x=8,
        doc="8个通道的温度值列表，单位℃",
        fget="read_channel_temps"
    )

    def init_device(self):
        """初始化设备"""
        Device.init_device(self)

        # 获取设备属性
        self.host = self.host
        self.port = int(self.port)
        self.slave_address = int(self.slave_address)
        self.temp_humidity_host = self.temp_humidity_host
        self.temp_humidity_port = int(self.temp_humidity_port)
        self.temp_humidity_slave_address = int(self.temp_humidity_slave_address)
        # 创建PK9019实例
        try:
            self.pk9019_device = PK9019(
                host=self.host,
                port=self.port,
                slave_address=self.slave_address
            )
            self.temp_humidity_device = TempHumidity(
                host=self.temp_humidity_host,
                port=self.temp_humidity_port,
                slave_address=self.temp_humidity_slave_address
            )
            self.set_state(DevState.ON)
            log.info(f"PK9019设备初始化成功: {self.host}:{self.port}")
            log.info(f"温度湿度设备初始化成功: {self.temp_humidity_host}:{self.temp_humidity_port}")
        except Exception as e:
            self.set_state(DevState.FAULT)
            log.error(f"设备初始化失败: {str(e)}")
            raise

    def read_environment_temp(self) -> float:
        """读取环境温度属性"""
        try:
            return self.pk9019_device.get_environment_temp()
        except Exception as e:
            log.error(f"读取环境温度失败: {str(e)}")
            self.set_state(DevState.FAULT)
            raise

    def read_channel_temps(self) -> list[float]:
        """读取通道温度属性"""
        try:
            temps = self.pk9019_device.get_all_temps()
            # 将'断线'转换为0.0
            return [0.0 if temp == '断线' else temp for temp in temps]
        except Exception as e:
            log.error(f"读取通道温度失败: {str(e)}")
            self.set_state(DevState.FAULT)
            raise
        
    def read_temp_humidity(self) -> tuple[float]:
        """读取温度湿度属性"""
        try:
            return self.temp_humidity_device.get_temp_humidity()
        except Exception as e:
            log.error(f"读取温度湿度失败: {str(e)}")
            self.set_state(DevState.FAULT)  