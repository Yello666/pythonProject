import json
import datetime
import os

from websockets import WebSocketClientProtocol


# 记录设备的状态数据
async def ws_update_device(ws: WebSocketClientProtocol, did: str, data):
    print("更新状态")
    await save_status_data(did, data)
    from South.ws_hearbeat import server_heartbeat_update
    await server_heartbeat_update(did)
    await ws.send(json.dumps({
        "method": "STATUS_DATA_UPLOAD",
        "type": "0",
        "data": {
            "status": "success",
            "message": "成功更新状态"
        }
    }))

# 直接在文件中追加写，文件路径为/status_data/{did}/{date}.json
async def save_status_data(did,data):
    # 获取当前日期并格式化
    current_date = datetime.datetime.today().strftime('%Y-%m-%d')
    # 拼接文件名
    file_url = f"./status_data/{did}/{current_date}.json"
    # 确保目录存在
    os.makedirs(os.path.dirname(file_url), exist_ok=True)
    # 追加写需要先读取现有的内容（如果文件存在）
    try:
        if os.path.exists(file_url):
            with open(file_url, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = []  # 如果文件不存在，初始化为空列表
    except json.JSONDecodeError:
        existing_data = []  # 处理文件格式错误，避免崩溃
    # 追加新数据
    existing_data.append(data)
    # 写回文件
    with open(file_url, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4)