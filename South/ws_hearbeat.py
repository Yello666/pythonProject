import asyncio
import json
from sanic.log import logger

from constant.redis_constant import server_heartbeat_token_key_prefix
from constant.heartbeat_constant import server_token_ttl, server_check_heartbeat_time
from constant import redis_constant, job_constant
from util.mysql_util import update_connection
from util.redis_util import *


# 发送心跳响应
async def send_resp(ws, did, status="success", message="收到心跳包"):
    data = json.dumps({
        "status": status,
        "message": message,
    })
    await ws.send(json.dumps({"did": did, "type": "0", "data": data, "method": "HEART_BEAT"}))


# 如果收到客户端心跳包说明连接正常，更新server_token并返回成功
async def ws_heartbeat_update(ws, data, did):
    try:
        # 接收上传的心跳包
        # 获取设备hardware_sn
        # 生成redis中的key
        print("收到心跳")
        await server_heartbeat_update(did)
        # 如果data不为None
        if data is not None:
            # 证明有状态数据上传，记录状态数据上传
            print("由心跳触发状态更新")
            from South.ws_update_device import save_status_data
            await save_status_data(did, data)
            # 刷新client中状态数据上报的key
            status_upload_key = redis_constant.client_status_data_upload_key_prefix + str(did)
            await set_token_connection(status_upload_key, job_constant.status_data_upload_times)
        await send_resp(ws, did)
    except json.JSONDecodeError:
        logger.error("收到的状态数据不是合法的 JSON 格式")
        await send_resp(ws, status="error", message="Invalid JSON")
        return
    except Exception as e:
        logger.error(f"WebSocket 异常：{e}")
        await ws.close()
        return

async def server_heartbeat_update(did):
    print("更新server_token")
    key = server_heartbeat_token_key_prefix + str(did)
    # 更新或者设置key
    await set_token_connection(key, server_token_ttl)



# server端维护心跳
async def ws_heartbeat_keep(did):
    # 获取server心跳token
    token_key = f"{server_heartbeat_token_key_prefix}{did}"
    # 初始化server_token
    await set_token_connection(token_key, server_token_ttl)
    # 将设备状态改为在线
    try:
        sql = "UPDATE device SET status = 0 WHERE did = %s"
        update_connection(sql, (did,))
    except Exception as e:
        logger.error(f"Error in update_device_by_did: {e}")
    while True:
        # 检查redis连接是否正常
        redis = await get_redis()
        if redis is None:
            raise RuntimeError('redis client is none')
        # 检查token是否还存在
        has_key = await has_token_connection(token_key)
        # 如果token不存在则说明对方离线，将对方token删除并将重连次数改为3次触发重连
        if not has_key:
            # 获取客户端key并删除
            key = f"{redis_constant.client_heartbeat_token_key_prefix}{did}"
            await delete_token_connection(key)
            # 构造心跳重试次数的key并更新为3
            retry_count_key = f"{redis_constant.client_heartbeat_retry_count_key_prefix}{did}"
            await set_retry_heartbeat_count_connection(retry_count_key, 3)
            print("客户端离线")
            # 更新数据库状态,将设备状态改为离线
            try:
                sql = "UPDATE device SET status = 1 WHERE did = %s"
                update_connection(sql, (did,))
            except Exception as e:
                logger.error(f"Error in update_device_by_did: {e}")
            return
        else:
            await asyncio.sleep(server_check_heartbeat_time)
