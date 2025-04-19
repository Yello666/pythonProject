#开启webSocket连接
import asyncio
import json

import psutil
import websockets
from websockets import ConnectionClosed

from biz_handler.biz_handler import biz_handler
from client_util import client_login
from client_util.client_heartbeat import heartbeat_handler
from client_util.client_instruction import  instruction_handler
from client_util.client_logger import logger
from client_util.client_device_data import accept_status_upload_response
from util.redis_util import *
from constant import heartbeat_constant, redis_constant

# 重连websocket的次数
websocket_reconnect_count = 0

# 心跳维持
async def ws_heartbeat_task(ws: websockets.WebSocketClientProtocol,did:str):
    # 初始化token
    # 获取token_key
    token_key = f"{redis_constant.client_heartbeat_token_key_prefix}{did}"
    # 在redis中添加token
    await set_token_connection(token_key, heartbeat_constant.client_token_ttl)
    print("心跳开始")
    while True:
        try:
            redis = await get_redis()
            if redis is None:
                raise RuntimeError('redis client is none')
            # 1.检测redis中token是否存在
            # 1.1构建key
            token_key = f"{redis_constant.client_heartbeat_token_key_prefix}{did}"
            # 1.2查找redis中token是否存在
            has_key = await has_token_connection(token_key)
            if not has_key:
                # 如果redis中不存在token
                # 2.获取状态数据上报key
                # 构造key
                status_data_upload_key = f"{redis_constant.client_status_data_upload_key_prefix}{did}"
                # 查询redis中key的过期时间
                ttl = await get_key_expire_time(status_data_upload_key)
                status_data = None
                if ttl == -2 or 0<ttl<=1:
                    # 3.获取状态数据
                    status_data = {}
                    # CPU利用率
                    cpu = psutil.cpu_percent(interval=1)
                    status_data['cpu'] = cpu
                    # 内存使用率
                    memery = psutil.virtual_memory()
                    status_data['memory'] = memery.percent
                    # 磁盘使用率
                    disk_use = psutil.disk_usage('/')
                    status_data['disk_usage'] = disk_use.percent
                    # 网络状况
                    # 获取所有网络接口的信息
                    network_info = psutil.net_if_addrs()
                    # 获取所有网络接口的状态
                    network_stats = psutil.net_if_stats()
                    network = {}
                    for interface in network_info:
                        network[interface] = {
                            'addresses': network_info[interface],  # 网络接口的地址信息
                            'status': network_stats.get(interface, None)  # 网络接口的状态（如是否启用、速度等）
                        }
                    status_data['network'] = network
                # 4.发送心跳
                request = {
                    "did": did,
                    "type":"0",
                    "method": "HEART_BEAT",
                    "data": status_data
                }
                #重试三次
                #构造心跳重试次数的key
                retry_count_key = f"{redis_constant.client_heartbeat_retry_count_key_prefix}{did}"
                retry_count = await get_retry_heartbeat_count_connection(retry_count_key)
                while retry_count < 3:
                    # 在redis中增加心跳重试次数
                    await incr_retry_heartbeat_count_connection(retry_count_key)
                    print(f"心跳第{retry_count}次重试")
                    # 超时时间设置为1s
                    await ws.send(json.dumps(request))
                    #阻塞1s用来等待回复
                    await asyncio.sleep(1)
                    #查询token是否存在，如果存在则说明心跳正常，退出检查
                    has_key = await has_token_connection(token_key)
                    if has_key:
                        # 删除重试次数
                        #retry_count_key = f"{redis_constant.client_heartbeat_retry_count_key_prefix}{did}"
                        await delete_token_connection(retry_count_key)
                        #退出检测
                        break
                    # 更新重试次数
                    retry_count = await get_retry_heartbeat_count_connection(retry_count_key)
                # 如果代码执行到这里，说明已经重试三次了，需要删除服务端redis中token和心跳重试次数的key，并重连
                if retry_count >= 3:
                    server_token_key = f"{redis_constant.client_heartbeat_token_key_prefix}{did}"
                    # 删除服务端redis中的token
                    await delete_token_connection(server_token_key)
                    # 删除心跳重试次数的key
                    await delete_token_connection(retry_count_key)
                    # 关闭连接触发重连
                    await ws.close()
                    return
                #到这里说明没触发重连，休眠
                await asyncio.sleep(heartbeat_constant.client_check_heartbeat_time)
            else:
                await asyncio.sleep(heartbeat_constant.client_check_heartbeat_time)
        except Exception as e:
            print(f"心跳错误{e}")
            await ws.close()
            break

# 状态数据上报
async def ws_status_data_upload(ws: websockets.WebSocketClientProtocol,did:str):
    # 1.检查redis中是否有状态数据上报的key
    # 构造key
    status_data_upload_key = f"{redis_constant.client_status_data_upload_key_prefix}{did}"
    # 查询redis中key的过期时间
    print("开始上报状态定时器")
    while True:
        try:
            ttl = await get_key_expire_time(status_data_upload_key)
            # 处理返回值
            if ttl == -2:
                # key 不存在，就要上报状态
                # 2.获取状态数据
                status_data = {}
                # CPU利用率
                cpu = psutil.cpu_percent(interval=1)
                status_data['cpu'] = cpu
                # 内存使用率
                memery = psutil.virtual_memory()
                status_data['memory'] = memery.percent
                # 磁盘使用率
                disk_use = psutil.disk_usage('/')
                status_data['disk_usage'] = disk_use.percent
                # 网络状况
                # 获取所有网络接口的信息
                network_info = psutil.net_if_addrs()
                # 获取所有网络接口的状态
                network_stats = psutil.net_if_stats()
                network = {}
                for interface in network_info:
                    network[interface] = {
                        'addresses': network_info[interface],  # 网络接口的地址信息
                        'status': network_stats.get(interface, None)  # 网络接口的状态（如是否启用、速度等）
                    }
                status_data['network'] = network
                # 3.发送状态数据
                request = {
                    "did": did,
                    "type": "0",
                    "method": "STATUS_DATA_UPLOAD",
                    "data": status_data
                }
                print("上报状态")
                await ws.send(json.dumps(request))
                await asyncio.sleep(1)
            elif ttl != -1:
                # 如果不是-1，休眠过期时间
                await asyncio.sleep(ttl)
            else:
                logger()
        except Exception as e:
            print(f"上报状态错误{e}")
            break


# 整个 client 的逻辑
async def start(url: str, hardware_sn: str, password: str):
    while True:
        try:
            async with websockets.connect(url) as ws:
                # 首次建立连接进行登陆验证
                await client_login.login(ws,hardware_sn, password)
                # 从服务端获取凭证，如果未获取说明连接错误
                message = await ws.recv()
                # 将数据转化为json
                msg = json.loads(message)
                # 如果未收到did凭证则视为连接不成功
                if "data" not in msg or "did" not in msg["data"]:
                    # 登录不成功，记录日志，断开连接
                    #根据data中反馈记录日志
                    logger()
                    await ws.close()
                    # 跳出循环
                    break
                else:
                    #global did
                    did = msg["data"]["did"]
                    # 这里就是登录成功要开始执行业务功能了
                    # 初始化 redis 连接
                    await init_redis_connect()
                    # 开启心跳定时器
                    asyncio.create_task(ws_heartbeat_task(ws,did))
                    # 开启状态上报定时器
                    asyncio.create_task(ws_status_data_upload(ws,did))
                    while True:
                        try:
                            #收到服务端消息并转化为易读
                            message= await ws.recv()
                            # 如果收到消息为心跳则刷新token
                            if message is not None:
                                msg = json.loads(message)
                                # 如果type是1说明为业务数据直接上传到业务层
                                msg_type = msg["type"]
                                if msg_type == "1":
                                    await biz_handler(msg)
                                else:
                                    method=msg["method"]
                                    if method == "HEART_BEAT":
                                        await heartbeat_handler(did,msg["data"])
                                    elif method == "INSTRUCTION":
                                        await instruction_handler(ws,did,msg["data"])
                                    elif method == "STATUS_DATA_UPLOAD":
                                        await accept_status_upload_response(did,msg["data"])
                        except ConnectionClosed :
                            print( "连接关闭,进行重新连接")
                            # 重连等待
                            await asyncio.sleep(5)
                            break
        except ConnectionRefusedError as e:
            global websocket_reconnect_count
            print(f"{e}连接错误")
            # 这里增加重新连接websocket次数
            if websocket_reconnect_count == 10:
                # 重连 10 次就认为服务端挂了
                return
            websocket_reconnect_count += 1
            await asyncio.sleep(5)
