import asyncio
import json
from asyncio import Lock

from sanic import Sanic, response
from sanic.exceptions import WebsocketClosed
from sanic.log import logger

# 导入每一个接口需要的函数
from North import (
    delete_device, get_device, add_device, update_device, change_psd,
    delete_group, get_group, add_group, update_group,
    get_relation, delete_relation, add_relation, delete_devices_by_gid, delete_group_by_did,
    get_group_did, get_device_gid, get_all0
)
from South.ws_instruction import recv_instruction_handler
from South.ws_log_handler import ws_device_log
# 新南向
from South.ws_login import ws_judge
from South.ws_update_device import ws_update_device
from South.ws_hearbeat import ws_heartbeat_keep, ws_heartbeat_update
from biz_handler.biz_handler import biz_handler
from constant.redis_constant import server_job_token_key_prefix, server_job_retry_count_key_prefix
from util.redis_util import init_redis_connect, close_redis_connect, get_redis, set_job_name_connection, \
    get_retry_job_count_connection, has_token_connection, incr_retry_job_count_connection, delete_token_connection

app = Sanic("device_manage")

# 设置错误的响应格式
app.config.FALLBACK_ERROR_FORMAT = "json"

# 用于存储所有 WebSocket 连接
connections = {}
# 用于存储所有设备的心跳检测任务
heartbeat_check_tasks = {}
# 锁，用于修改 connections
lock = Lock()


@app.before_server_start
async def before_server_start(app, loop):
    # 初始化 redis 客户端
    await init_redis_connect()


@app.after_server_stop
async def after_server_stop(app, loop):
    # 关闭 redis 客户端
    await close_redis_connect()


# device
# 根据did或者设备型号与序列号SN组合查询device，无提供参数则查询所有device
@app.get("/v1/devices", ignore_body=False)
async def get_devices(request):
    return await get_device.get_devices(request)


# 自动生成did与PWD，并与提供信息一起作为device设备添加到数据库中
@app.post("/v1/devices")
async def add_devices(request):
    return await add_device.add_devices(request)


# 根据提供did更新device信息
@app.put("/v1/devices")
async def update_devices(request):
    return await update_device.update_devices(request)


# 根据提供did将设备状态置为删除
@app.delete("/v1/devices")
async def delete_devices(request):
    return await delete_device.delete_devices(request)


# ?根据gid查询信息 或者不提供参数查询所有组 无信息咋办？
@app.get("/v1/group", ignore_body=False)
async def get_devices_group(request):
    return await get_group.get_groups(request)


# 自动生成gid并将数据添加到数据库
@app.post("/v1/group")
async def add_devices_group(request):
    return await add_group.add_groups(request)


# 根据gid与提供的新gname修改数据
@app.put("/v1/group")
async def update_devices_group(request):
    return await update_group.update_groups(request)


# 根据提供gid将状态置为删除
@app.delete("/v1/group")
async def delete_devices_group(request):
    return await delete_group.delete_groups(request)


# 修改设备密码
@app.put("/v1/psd")
async def update_devices_psd(request):
    return await change_psd.change_psd(request)


# 根据gid与did查询设备是否属于该分组
@app.get("/v1/relation")
async def get_relation_func(request):
    return await get_relation.get_relation1(request)


# 根据提供gid与did删除分组关系
@app.delete("v1/relation")
async def delete_relation_func(request):
    return await delete_relation.delete_relation1(request)


# 根据提供gid与did增加分组关系
@app.put("/v1/relation")
async def add_relation_func(request):
    return await add_relation.add_relation1(request)


# 根据提供gid将gid分组内所有设备删除并更新状态
@app.delete('v1/group_device')
async def delete_devices_by_gid_func(request):
    return await delete_devices_by_gid.delete_devices_by_gid1(request)


# 根据提供did将所有有关系的组删除
@app.delete("v1/device_group")
async def delete_group_by_did_func(request):
    return await delete_group_by_did.delete_group_by_did1(request)


# 根据提供did查询所有有关系的组
@app.get("v1/device_group")
async def get_group_by_did(request):
    return await get_group_did.get_group_by_did(request)


# 根据提供gid查询组内所有设备
@app.get("v1/group_device")
async def get_device_by_gid(request):
    return await get_device_gid.get_device_by_gid(request)


# 根据提供did查询did及其有关组的所有信息，如果未提供参数则返回所有设备及其有关组信息
@app.get("v1/all")
async def get_all(request):
    return await get_all0.get_all1(request)


# 暴露给业务服务，让业务服务调用这个接口去下发框架外指令
@app.post("/v1/instruction")
async def instruction(request):
    return await issue_instruction(request)


# 服务端主动发送指令
async def issue_instruction(request):
    # 将data转化为字典
    data = request.json
    # 从request 中读取did和指令
    did = data["did"]
    instruction = data["instruction"]
    # 获取job的名字来判断是否为框架外
    job_name = instruction["job_name"]
    # 获取判断用job_token的key并设立
    token_key = f"{server_job_token_key_prefix}:{did}:{job_name}"
    await set_job_name_connection(token_key)
    # 如果是reboot或者sftp则为框架内
    type = 0 if job_name == "reboot" or job_name == "sftp" else 1
    if did is not None and did in connections:
        ws = connections[did]
        # 判断是否指令是否发送成功，不成功则重试
        # 获取重试指令次数key
        count_token_key = f"{server_job_retry_count_key_prefix}:{did}:{job_name}"
        retry_job_count = await get_retry_job_count_connection(count_token_key)
        while retry_job_count < 3:
            # 下发指令
            await ws.send(json.dumps({
                "method": "INSTRUCTION",
                "data": instruction,
                "type": type
            }))
            # 等待指令执行并反馈 Todo 多少秒合适
            await asyncio.sleep(30)
            # 判断是否执行成功
            has_key = await has_token_connection(token_key)
            if has_key:
                await incr_retry_job_count_connection(count_token_key)
                retry_job_count = await get_retry_job_count_connection(count_token_key)
            # 不存在说明执行成功
            else:
                print("执行命令成功")
                await delete_token_connection(count_token_key)
                return response.json(
                    {
                        "status": 200,
                        "message": "执行成功",
                    }
                )
        else:
            logger.error(f"客户端{did}执行指令失败")
            await delete_token_connection(count_token_key)
            return response.json(
                {
                    "status": 200,
                    "message": "执行失败",
                }
            )
    else:
        logger.error(f"客户端 {did} 不在线.")


# 维护与每个客户端的连接
@app.websocket("/v1/ws/<hardware_sn>")
async def ws_handler(request, ws, hardware_sn):
    # 处理客户端发送来的消息
    print(f"{hardware_sn}开始连接")
    try:
        while True:
            # 接收客户端传递的信息
            message = await ws.recv()
            # ws.send(message)
            # 将数据转化为json
            msg = json.loads(message)
            if "did" not in msg:
                # 如果did与sn均为提供则视为无效连接
                if "hardware_sn" not in msg:
                    await ws.send(json.dumps({
                        "data": {
                            "status": "error",
                            "message": "未登录"
                        },
                        "type": "0",
                    }))
                # 未提供did但是提供sn视为首次登陆连接
                # 判断sn序列号是否为有效序列号,验证密码是否正确
                elif "hardware_sn" in msg:
                    data = msg["data"]
                    sn = msg["hardware_sn"]
                    pwd = data["password"]
                    # 设备登录验证，如果验证成功会返回did，失败会返回""
                    did = await ws_judge(sn, pwd)
                    if did is None or did == "":
                        await ws.send(json.dumps({
                            "data": {
                                "status": "error",
                                "message": "验证失败"
                            },
                            "type": "0",
                        }))
                    else:
                        print(did)
                        await ws.send(json.dumps({
                            "data": {"did": did,
                                     "status": "success",
                                     "message": "验证成功"
                                     },
                            "type": "0",
                        }))
                        # 启动一个心跳检测任务，将这个任务放入任务池中
                        heartbeat_check_tasks[did] = asyncio.create_task(ws_heartbeat_keep(did))
                        print("心跳开始")
                        # 将成功的ws连接放进连接池中
                        connections[did] = ws
            # 提供did说明为有效连接
            else:
                type = msg["type"]
                # 如果为业务消息直接传递给业务处理函数
                if type == "1":
                    await biz_handler(msg)
                else:
                    method = msg["method"]
                    # 客户端上报的状态数据
                    if method == "STATUS_DATA_UPLOAD":
                        await ws_update_device(ws, msg["did"], msg["data"])
                    # 处理客户端执行指令的结果
                    elif method == "INSTRUCTION":
                        await recv_instruction_handler(msg["data"], msg["did"])
                    # 心跳处理
                    elif method == "HEART_BEAT":
                        await ws_heartbeat_update(ws, msg["data"], msg["did"])
                    # 客户端上报的日志
                    elif method == "DEVICE_LOG":
                        await ws_device_log()
    except WebsocketClosed:
        logger.error("客户端断开连接.")
    finally:
        # 从连接字典中移除断开的连接
        # 加锁保证并发安全
        async with lock:
            connections.pop(hardware_sn, None)
            # 关闭所有协程（心跳）
            if heartbeat_check_tasks[did] is not None:
                heartbeat_check_tasks[did].cancel()
            logger.info(f"Client {hardware_sn} removed. Total clients: {len(connections)}")


# 独立线程运行及重启服务
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, single_process=True)
