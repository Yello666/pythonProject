from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR
from datetime import datetime

#根据did查询对应的所有设备组信息
async def get_group_by_did(request):
    did = request.args.get('did')
    if not did:
        return response.json(
            {
                "status": 0,
                "message": "没有合法did"
            }
        )
    sql1 = "select gid from relation where did = %s and r_status = 0"
    try:
        results = SQLR.select_connection_all1(sql1, (did,))
    except Exception as e:
        logger.error(f"Error in handle_gid: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error retrieving device group"
            }
        )
    if not results:
        return response.json(
            {
                "status": 0,
                "message": "该设备没有分组"
            }
        )
    groups = []
    for result in results:
        gid = result[0]
        sql2 = "select * from device_group where gid = %s and g_status = 0"
        try:
            results1 = SQLR.select_connection_one(sql2, (gid,))
        except Exception as e:
            logger.error(f"Error in handle_gid: {e}")
            return response.json(
                {
                    "status": 0,
                    "message": "Error retrieving device group"
                }
            )
        if results1 is None:
            return response.json(
                {
                    "status": 0,
                    "message": "对应的分组不存在"
                }
            )
        group = {
            "gid": results1[0],
            "gname": results1[1],
            # "g_created_time": datetime.utcfromtimestamp(results1[2] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            # "g_last_update": datetime.utcfromtimestamp(results1[3] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "g_created_time": results1[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "g_last_update": results1[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        }
        groups.append(group)
    return response.json(
        {
            "status": 200,
            "message": "查询成功",
            "group": groups
        }
    )
