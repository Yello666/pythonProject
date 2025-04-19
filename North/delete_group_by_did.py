from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR


async def delete_group_by_did1(request):
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
    sql1 = "select gid from relation where did = %s and r_status = 0"
    try:
        results = SQLR.select_connection_all1(sql1, (did,))
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
                "message": "该设备没有分组"
            }
        )
    for row in results:
        gid = row[0]
        try:
            sql2 = "UPDATE device_group SET g_status = 1 WHERE gid = %s"
            sql3 = "UPDATE relation SET r_status = 1 WHERE gid = %s and did = %s"

            SQLR.delete_connection(sql2, (gid,))
            SQLR.delete_connection(sql3, (gid, did))

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
            "message": "分组删除成功"
        }
    )
