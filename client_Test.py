import asyncio
import sys

from client_util import client_start

# 启动程序时附加当前设备序列号,服务端的的地址，设备密码
ip = sys.argv[1]
port = sys.argv[2]
hardware_sn = sys.argv[3]
password = sys.argv[4]
# 通过hardware_sn进行webSocket连接
ws_url = f"ws://{ip}:{port}/v1/ws/{hardware_sn}"

asyncio.run(client_start.start(ws_url,hardware_sn,password))