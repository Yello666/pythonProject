from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR


async def delete_devices_by_gid1(request):
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
    sql1 = "select did from relation where gid = %s and r_status = 0"
    try:
        results = SQLR.select_connection_all1(sql1, (gid,))
    except Exception as e:
        logger.error(f"Error in delete_devices: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error deleting device groups"
            }
        )
    if not results:
        return response.json(
            {
                "status": 0,
                "message": "该组内没有添加设备"
            }
        )
    for row in results:
        did = row[0]
        try:
            # 逻辑删除
            sql2 = "UPDATE device SET status = 2 WHERE did = %s"
            sql3 = "UPDATE relation SET r_status = 1 WHERE did = %s and gid = %s"

            SQLR.delete_connection(sql2, (did,))
            SQLR.delete_connection(sql3, (did, gid))

        except Exception as e:
            logger.error(f"Error in delete_device_by_did: {e}")
            return response.json(
                {
                    "status": 0,
                    "message": "Error deleting device"
                }
            )

    return response.json(
        {
            "status": 200,
            "message": "设备删除成功"
        }
    )
