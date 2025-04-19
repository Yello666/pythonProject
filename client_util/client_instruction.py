# 对框架内指令进行处理
import json

from client_util.client_heartbeat import client_heartbeat_update


async def instruction_handler(ws,did,data):
    # Todo reboot以及sftp

    # 以下为测试接口代码
    print("成功执行指令")
    # 成功执行指令说明业务往来，更新心跳
    await client_heartbeat_update(did)
    await ws.send(json.dumps({
        "did": did,
        "method": "INSTRUCTION",
        "type":"0",
        "data":{
            "status":"success",
            "job_name":data["job_name"]
        }
    }))
