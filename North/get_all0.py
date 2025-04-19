from sanic import response
from datetime import datetime
from sanic.log import logger
from util import mysql_util as SQLR

#更新并获取指定did的所有组信息,如果没有did就更新并获取所有设备的组信息
async def get_all1(request):
    did = request.args.get('did')
    if did:
        return await get_all_did(did)
    elif len(request.args) == 0:
        return await get_all_none()
    else:
        return response.json(
            {
                "status": 0,
                "message": "url输入错误"
            }
        )


async def get_all_did(did):
    # 查询所有与did有关的组
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
        # 查询所有有关组的信息
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
        group = { # 格式化组信息,为后面返回data时做准备
            "gid": results1[0],
            "gnum": results1[1],
            # "g_created_time": datetime.utcfromtimestamp(results1[2] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            # "g_last_update": datetime.utcfromtimestamp(results1[3] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            # 不能对 datetime.datetime 类型进行除法操作
            "g_created_time": results1[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "g_last_update": results1[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        }
        groups.append(group)

    # groups信息插入device
    sql3 = "select * from device where did = %s and status != 2"
    value = (did,)
    try:
        results3 = SQLR.select_connection_one(sql3, value)
    except Exception as e:
        # logger.error(f"Error in add_devices: {e}")
        # return response.json(
        #     {
        #         "status": 0,
        #         "message": "Error adding device, group, and relation"
        #     }
        # )
        logger.error(f"Error in get_all: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error querying device"
            }
        )
    if results3 is None:
        return response.json(
            {
                "status": 0,
                "message": "数据库没有对应数据"
            }
        )

    device = {
        "did": results3[0],
        "dname": results3[1],
        # "d_created_time": datetime.utcfromtimestamp(results3[2] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        # "d_last_update": datetime.utcfromtimestamp(results3[3] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        # 不能对 datetime.datetime 类型进行除法操作
        "d_created_time": results3[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "d_last_update": results3[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "hardware_sn": results3[4],
        "hardware_model": results3[5],
        "nic_type": results3[6],
        "nic_ipv4": results3[7],
        "nic_mac": results3[8],
        "wifi_mac": results3[9],
        "LTE_IMEI": results3[10],
        "software_version": results3[13],
        "software_last_update": results3[14].strftime('%Y-%m-%d %H:%M:%S'),
        "status": results3[15],
        "groups": groups
    }
    return response.json(
        {
            "status": 1,
            "message": "获取设备成功",
            "data": [device]
        })


async def get_all_none():
    # 查询所有的设备的组信息
    sql0 = "select * from device where status != 2"
    try:
        results0 = SQLR.select_connection_all(sql0)
    except Exception as e:
        # logger.error(f"Error in add_devices: {e}")
        # return response.json(
        #     {
        #         "status": 0,
        #         "message": "Error adding device, group, and relation"
        #     }
        # )
        logger.error(f"Error in get_all: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error querying device"
            }
        )
    if results0 is None:
        return response.json(
            {
                "status": 0,
                "message": "数据库没有设备"
            }
        )
    devices = []
    # 遍历设备信息，查询设备的分组id
    for row in results0:
        did = row[0]
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
        groups = []
        if results:
            # 再通过设备的分组id，查询设备的分组信息
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
                    continue
                group = {
                    "gid": results1[0],
                    "gname": results1[1],
                    # "g_created_time": datetime.utcfromtimestamp(results1[2] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[
                    #                   :-3],
                    # "g_last_update": datetime.utcfromtimestamp(results1[3] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[
                    #                  :-3],
                    # 不能对 datetime.datetime 类型进行除法操作
                    "g_created_time": results1[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "g_last_update": results1[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                }
                groups.append(group)

        device = {
            "did": row[0],
            "dname": row[1],
            # "d_created_time": datetime.utcfromtimestamp(results[2] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            # "d_last_update": datetime.utcfromtimestamp(results[3] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            # 不能对 datetime.datetime 类型进行除法操作
            "d_created_time": row[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "d_last_update": row[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "hardware_sn": row[4],
            "hardware_model": row[5],
            "nic_type": row[6],
            "nic_ipv4": row[7],
            "nic_mac": row[8],
            "wifi_mac": row[9],
            "LTE_IMEI": row[10],
            "software_version": row[13],
            "software_last_update": row[14].strftime('%Y-%m-%d %H:%M:%S'),
            "status": row[15],
            "groups": groups
        }
        devices.append(device)
    return response.json({
        "status": 1,
        "message": "获取数据成功",
        # "devices": devices
        "data": devices #更改了成功之后的返回信息与前面保持一致
    })
