from South.ws_hearbeat import server_heartbeat_update
from constant.redis_constant import server_job_token_key_prefix
from util.redis_util import delete_token_connection


async def recv_instruction_handler(data,did):
    if data["status"] == "success":
        #业务往来成功说明心跳正常
        print("收到指令成功信息")
        await server_heartbeat_update(did)
        # 获取token_key
        token_key = f"{server_job_token_key_prefix}:{did}:{data['job_name']}"
        # 在redis中删除token
        await delete_token_connection(token_key)

