from client_util.client_heartbeat import client_heartbeat_update
from constant import redis_constant, job_constant
from util.redis_util import set_token_connection


# 接受状态上报的响应，刷新redis中状态上报的key过期时间
async def accept_status_upload_response(did, data):
    if data["status"] == "success":
        print("上报状态成功")
        # 上报状态成功说明心跳正常，更新心跳
        await client_heartbeat_update(did)
        # 获取key
        key = f"{redis_constant.client_status_data_upload_key_prefix}{did}"
        # 在redis中添加token
        await set_token_connection(key, job_constant.status_data_upload_times)
