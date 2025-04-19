# 登陆验证函数
import json

async def login(ws,hardware_sn, password):
    await ws.send(json.dumps({
        "hardware_sn": hardware_sn,
        "data":{"password": password}
    }))
