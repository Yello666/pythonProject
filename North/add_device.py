from sanic import response
import time
from snowflake import SnowflakeGenerator
from sanic.log import logger
from util import mysql_util as SQLR
import hashlib
import random
import string
from datetime import datetime

# 雪花算法实例
gen = SnowflakeGenerator(1)


# 随机生成密码
def generate_password(length=10):
    # string.ascii_letters包含所有大小写字母, string.digits包含所有数字
    all_chars = string.ascii_letters + string.digits
    # 在all_chars中随机选择十个字符组成密码
    password = ''.join(random.choice(all_chars) for _ in range(length))
    return password


# 生成一个盐值
def generate_salt(length=10):
    salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return salt


# 使用sha256散列函数进行加盐散列
def hash_password(password, salt):
    m = hashlib.sha256()
    # 先放入盐值，再放入密码
    m.update(salt.encode()) #将字符串 salt 编码为字节类型,并更新到哈希对象 m 中
    m.update(password.encode()) #将盐值和用户的密码拼接在一起,使用散列函数对拼接后的字符串进行散列计算
    # 返回16进制表示的散列值
    return m.hexdigest() #获取当前哈希对象的哈希值，并将其转换为十六进制字符串形式


async def add_devices(request):
    data = request.json

    # 生成设备信息
    # 使用雪花算法生成id，即设备编号
    did = next(gen)
    # 真实密码
    password = generate_password()
    # 设备的名称，data是存放了设备信息的字典，通过get（键值）可以获取对应的value
    dname = data.get('name')
    # 创建时间时间戳
    curTime = time.time()
    d_created_time = datetime.fromtimestamp(curTime)
    # 修改时间时间戳
    d_last_update = datetime.fromtimestamp(curTime)
    # 硬件序列号SN
    hardware_sn = data.get('hardware_sn')
    # 硬件型号Model
    hardware_model = data.get('hardware_model')
    # 网卡类型
    nic_type = data.get('nic_type')
    # 网卡MAC地址
    nic_mac = data.get('nic_mac')
    # 网卡IPv4
    nic_ipv4 = data.get('nic_ipv4')
    # WIFI网卡MAC地址
    wifi_mac = data.get('wifi_mac')
    # LTE IMEI编码，SIM 卡唯一标识
    LTE_IMEI = data.get('LTE_IMEI')
    # 加密盐
    salt = generate_salt()
    # 哈希散列处理密码+盐
    secret = hash_password(password, salt)
    # 驱动程序版本
    software_version = data.get('software_version')
    # 驱动程序更新时间
    software_last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 设备状态
    # 0启用
    # 1禁用
    # 2删除
    status = int(data.get('status'))

    # 要插入数据库的值，在上面data.get()已经取得
    values = (
    did, dname, d_created_time, d_last_update, hardware_sn, hardware_model, nic_type, nic_mac, nic_ipv4, wifi_mac,
    LTE_IMEI, salt, secret, software_version, software_last_update, status)

    # 构建sql语句
    sql = """INSERT INTO device(did, dname, d_created_time, d_last_update, hardware_sn, hardware_model, nic_type, nic_mac, nic_ipv4, wifi_mac, lte_imei, salt, secret, software_version, software_last_update, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    try:
        # 执行插入操作
        SQLR.insert_connection(sql, values)
        print(f"数据已添加，device_did为{did},密码为{password}")
        return response.json(
            {
                "status": 200,
                "message": "添加成功",
                "device_id": did,
                "device_password": password
            }
        )
    except Exception as e:
        logger.error(f"Error in add_devices: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error adding device, group, and relation"
            }
        )
