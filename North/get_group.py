from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR
from datetime import datetime

# 根据gid来找设备组信息
async def handle_gid(gid):
    sql1 = "select * from device_group where gid = %s and g_status = 0"
    value = (gid,)
    try:
        results = SQLR.select_connection_one(sql1, value)
    except Exception as e:
        logger.error(f"Error in handle_gid: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error retrieving device group"
            }
        )

    if results is None:
        return response.json(
            {
                "status": 0,
                "message": "Database has no corresponding data for the specified gid"
            }
        )

    # 错误逻辑，组序列是唯一的，不能获取到多个组信息
    # groups = []
    # for row in results:
    #     group = {
    #         "gid": row[0],
    #         "gname": row[1],
    #         # "g_created_time": datetime.utcfromtimestamp(row[2] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
    #         # "g_last_update": datetime.utcfromtimestamp(row[3] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
    #         #修改datetime对象进行除法运算的错误
    #         "g_created_time": row[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
    #         "g_last_update": row[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],

    #     }
    #     groups.append(group)

    # return response.json(
    #     {
    #         "status": 1,
    #         "message": "Device group retrieved successfully",
    #         "data": groups
    #     }
    # )
    # 处理单行数据
    group = {
        "gid": results[0],
        "gname": results[1],
        "g_created_time": results[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "g_last_update": results[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
    }

    return response.json(
        {
            "status": 1,
            "message": "Device group retrieved successfully",
            "data": [group]
        }
    )


async def handle_no_group_params():
    sql2 = "select * from device_group where g_status = 0"
    try:
        results = SQLR.select_connection_all(sql2)
    except Exception as e:
        logger.error(f"Error in handle_no_group_params: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error retrieving device groups"
            }
        )

    groups = []
    for row in results:
        group = {
            "gid": row[0],
            "gname": row[1],
            # "g_created_time": datetime.utcfromtimestamp(row[2] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            # "g_last_update": datetime.utcfromtimestamp(row[3] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "g_created_time": row[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "g_last_update": row[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        }
        groups.append(group)

    return response.json(
        {
            "status": 1,
            "message": "Device groups retrieved successfully",
            "data": groups
        }
    )


async def get_groups(request):
    gid = request.args.get('gid')
    if gid:
        # 根据gid查找设备组
        return await handle_gid(gid)
    elif len(request.args) == 0:
        return await handle_no_group_params()
    else:
        return response.json(
            {
                "status": 0,
                "message": "Error: 不合规范的url"
            },
            status=400  # Bad Request
        )
