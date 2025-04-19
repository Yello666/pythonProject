from datetime import datetime

from sanic import response
import time
from sanic.log import logger
from util import mysql_util as SQLR

#添加设备进设备组
async def add_relation1(request): # 拿到gid和did
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
    # status=2表示设备已经删除，0是启用 1是禁用
    sql1 = "select * from device where did = %s and status != 2"
    # g_status=0 是已经添加的设备组
    sql2 = "select * from device_group where gid = %s and g_status = 0"
    try:
        dide = SQLR.is_exist(sql1, (did,)) # 函数返回一个布尔值，表示是否能查询到该设备
        gide = SQLR.is_exist(sql2, (gid,))
    except Exception as e:
        logger.error(f"Error in update_groups: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error updating device group0"
            }
        )
    if not gide:
        return response.json(
            {
                "status": 0,
                "message": "group不存在"
            }
        )
    if not dide:
        return response.json(
            {
                "status": 0,
                "message": "device不存在"
            }
        )
    # 在relation表中查找是否存在gid和did这一组，如果存在说明该设备已在组中，没有必要重复添加
    sql3 = "select * from relation where did = %s and gid = %s and r_status = 0" # r_status = 0表示有关系
    try:
        result = SQLR.is_exist(sql3, (did, gid))
    except Exception as e:
        logger.error(f"Error in update_groups: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error updating device group1"
            }
        )
    if result:
        return response.json(
            {
                "status": 0,
                "message": "该设备已存在于分组中"
            }
        )
    # 此时gid did均存在且之前并没有添加过关系，可以添加关系，表明did标识的设备属于gid这一组
    # r_status=0表明有关系,r_status=1表示无关系
    sql4 = "INSERT INTO relation(did,gid,r_created_time,r_last_update,r_status) VALUES (%s, %s, %s, %s, %s);"
    # 创建时间时间戳
    curTime = time.time()
    r_created_time = datetime.fromtimestamp(curTime)
    # 修改时间时间戳
    r_last_update = datetime.fromtimestamp(curTime)
    values = (did, gid, r_created_time, r_last_update, 0)
    try:
        SQLR.insert_connection(sql4, values)
        return response.json(
            {
                "status": 200,
                "message": "设备添加分组成功"
            }
        )
    except Exception as e:
        logger.error(f"Error in update_groups: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error updating device group2"
            }
        )
