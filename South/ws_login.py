import json

from North.add_device import hash_password
from util import mysql_util

# 设备登录验证
async def ws_judge(hardware_sn:str,password:str)->str:
    device_info = mysql_util.get_info_by_sn(hardware_sn)
    if device_info is None:
        return ""
    if device_info["salt"] is None or device_info["secret"] is None or hash_password(password,device_info["salt"]) != device_info["secret"]:
        return ""
    return device_info["did"]
