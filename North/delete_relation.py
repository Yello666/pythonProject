from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR


async def delete_relation1(request):
    data = request.json
    did = data.get('did')
    gid = data.get('gid')
    if not did or not gid:
        return response.json(
            {
                "status": 0,
                "message": "没有指定的did与gid"
            },
            status=400  # Bad Request
        )
    sql1 = "select * from device where did = %s and status != 2"
    sql2 = "select * from device_group where gid = %s and g_status = 0"
    try:
        dide = SQLR.is_exist(sql1, (did,))
        gide = SQLR.is_exist(sql2, (gid,))
    except Exception as e:
        # logger.error(f"Error in update_groups: {e}")
        # return response.json(
        #     {
        #         "status": 0,
        #         "message": "Error updating device group"
        #     }
        # )
        logger.error(f"Error in delete_relation: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error querying device or group"
            }
        )
    if not dide or not gide:
        return response.json(
            {
                "status": 0,
                "message": "device或group不存在"
            }
        )
    #sql = "UPDATE device_group SET g_status = 1 WHERE gid = %s"
    sql="UPDATE relation SET r_status = 1 WHERE did = %s and gid = %s"
    values = (did, gid)
    try:
        SQLR.delete_connection(sql, values)
        return response.json(
            {
                "status": 200,
                "message": "设备分组信息删除成功"
            }
        )
    except Exception as e:
        # logger.error(f"Error in update_groups: {e}")
        # return response.json(
        #     {
        #         "status": 0,
        #         "message": "Error updating device group"
        #     }
        # )
        logger.error(f"Error in delete_relation: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error deleting relation between the specified device and group"
            }
        )
