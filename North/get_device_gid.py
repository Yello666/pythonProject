from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR
from datetime import datetime


async def get_device_by_gid(request):
    gid = request.args.get('gid')
    if not gid:
        return response.json(
            {
                "status": 0,
                "message": "没有合法gid"
            }
        )
    sql1 = "select did from relation where gid = %s and r_status != 1"

    try:
        results = SQLR.select_connection_all1(sql1, (gid,))
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
                "message": "该分组没有设备"
               
            }
        )
    devices = []
    for result in results:
        did = result[0]
        sql2 = "select * from device where did = %s and status != 2"
        try:
            results1 = SQLR.select_connection_one(sql2, (did,))
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
                    "message": "对应的设备不存在"
                }
            )
        device = { #进行了修改，results[]->results1[]
            "did": results1[0],
            "dname": results1[1],
            # "d_created_time": datetime.utcfromtimestamp(results1[2] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            # "d_last_update": datetime.utcfromtimestamp(results1[3] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            # 不能对 datetime.datetime 类型进行除法操作
            "d_created_time": results1[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "d_last_update": results1[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "hardware_sn": results1[4],
            "hardware_model": results1[5],
            "nic_type": results1[6],
            "nic_ipv4": results1[7],
            "nic_mac": results1[8],
            "wifi_mac": results1[9],
            "LTE_IMEI": results1[10],
            "software_version": results1[13],
            "software_last_update": results1[14].strftime('%Y-%m-%d %H:%M:%S'),
            "status": results1[15],
        }
        devices.append(device)
    return response.json(
        {
            "status": 1,
            "message": "获取设备成功",
            "data": devices
        })
