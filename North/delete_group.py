from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR


async def delete_groups(request):
    try:
        data = request.json
        gid = data.get('gid')

        if not gid:
            return response.json(
                {
                    "status": 0,
                    "message": "Error: Missing 'gid' parameter"
                },
                status=400  # Bad Request
            )

        # 删除设备分组信息
        sql1 = "UPDATE device_group SET g_status = 1 WHERE gid = %s"
        SQLR.delete_connection(sql1, (gid,))
        sql2 = "UPDATE relation SET r_status = 1 WHERE gid = %s"
        SQLR.delete_connection(sql2, (gid,))

        return response.json(
            {
                "status": 1,
                "message": "Device group deleted successfully"
            }
        )
    except Exception as e:
        logger.error(f"Error in delete_group: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error deleting device group"
            }
        )


# 根据设备编号删除全部所属分组 ?
async def delete_devices(request):
    try:
        data = request.json
        did = data.get('did')

        if not did:
            return response.json(
                {
                    "status": 0,
                    "message": "Error: Missing 'did' parameter"
                },
                status=400  # Bad Request
            )

        # 删除设备分组关联信息
        sql = "UPDATE relation SET r_status = 1 WHERE did = %s"
        SQLR.delete_connection(sql, (did,))

        return response.json(
            {
                "status": 1,
                "message": "All groups for the device deleted successfully"
            }
        )
    except Exception as e:
        logger.error(f"Error in delete_devices: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error deleting device groups"
            }
        )
