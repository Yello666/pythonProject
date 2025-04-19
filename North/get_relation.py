from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR

#根据did和gid查询relation表
async def get_relation1(request):
    # print(进来了)
    did = request.args.get('did')
    gid = request.args.get('gid')
    if not did or not gid:
        return response.json(
            {
                "status": 0,
                "message": "Error: 不合规范的url"
            },
            status=400  # Bad Request
        )
    # 判断是否存在did对应的设备和gid对应的设备组
    sql1 = "select * from device where did = %s and status != 2"
    sql2 = "select * from device_group where gid = %s and g_status = 0"
    try:
        dide = SQLR.is_exist(sql1, (did,))
        gide = SQLR.is_exist(sql2, (gid,))
    except Exception as e:
        logger.error(f"Error in update_groups: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error updating device group"
            }
        )
    if not dide or not gide:
        return response.json(
            {
                "status": 0,
                "message": "device或group不存在"
            }
        )
    # 查询relation表是否存在这样一对did和gid
    sql = "select * from relation where did = %s and gid = %s and r_status = 0"
    values = (did, gid)
    try:
        results = SQLR.is_exist(sql, values)
    except Exception as e:
        logger.error(f"Error in add_devices: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error adding device, group, and relation"
            }
        )
    if results:
        return response.json(
            {
                "status": 200,
                "is_relation_exist": results,
                "message": "该设备存在于分组中"
            }
        )
    else:
        return response.json(
            {
                "status": 200,
                "is_relation_exist": results,
                "message": "该设备不存在于分组中"
            }
        )
