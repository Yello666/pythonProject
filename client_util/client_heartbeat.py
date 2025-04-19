import json

from constant import redis_constant, heartbeat_constant
from util.redis_util import set_token_connection


async def heartbeat_handler(did,data):
    data=json.loads(data)
    if data["status"] == "success":
        print("有心跳机制本身触发心跳更新")
        await client_heartbeat_update(did)

async def client_heartbeat_update(did):
    print("刷新client_token")
    # 获取token_key
    token_key = f"{redis_constant.client_heartbeat_token_key_prefix}{did}"
    # 在redis中添加token
    await set_token_connection(token_key, heartbeat_constant.client_token_ttl)