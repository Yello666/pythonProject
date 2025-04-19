from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR
from datetime import datetime


async def update_groups(request):
    data = request.json

    gid = data.get('gid')
    new_gname = data.get('new_gname')  # 新的设备分组名称

    if not gid or not new_gname:
        return response.json(
            {
                "status": 0,
                "message": "Missing required parameters"
            },
            status=400  # Bad Request
        )

    # 构建 SQL 语句
    g_last_update = int(datetime.now().timestamp() * 1000)
    sql = "UPDATE device_group SET gname = %s, g_last_update = %s WHERE gid = %s and g_status = 0"
    values = (new_gname, g_last_update, gid)

    try:
        # 执行更新操作
        SQLR.update_connection(sql, values)
        return response.json(
            {
                "status": 1,
                "message": "Device group updated successfully"
            }
        )
    except Exception as e:
        logger.error(f"Error in update_groups: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error updating device group"
            }
        )
