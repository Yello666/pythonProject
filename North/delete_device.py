from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR


# 基于设备编号删除设备
async def delete_device_by_did(did):
    try:
        sql1 = "UPDATE device SET status = 2 WHERE did = %s"
        sql2 = "UPDATE relation SET r_status = 1 WHERE did = %s"

        SQLR.delete_connection(sql1, (did,))
        SQLR.delete_connection(sql2, (did,))

        return response.json(
            {
                "status": 200,
                "message": f"Device with did {did} deleted successfully"
            }
        )
    except Exception as e:
        logger.error(f"Error in delete_device_by_did: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error deleting device"
            }
        )


async def delete_devices(request):
    try:
        data = request.json
        did = data.get('did')

        if not did:
            return response.json(
                {
                    "status": 0,
                    "message": "Missing 'did' parameter in the request"
                },
                status=400  # Bad Request
            )
        # 表示等函数结果返回之后再return
        return await delete_device_by_did(did)
    except Exception as e:
        logger.error(f"Error in delete_devices: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error deleting device"
            }
        )
