from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR
from datetime import datetime


async def handle_did(did):
    sql1 = "select * from device where did = %s and status != 2"
    value = (did,)
    try:
        results = SQLR.select_connection_one(sql1, value)
    except Exception as e:
        logger.error(f"Error in add_devices: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error adding device, group, and relation"
            }
        )
    if results is None:
        return response.json(
            {
                "status": 0,
                "message": "数据库没有对应数据"
            }
        )

    device = {
        "did": results[0],
        "dname": results[1],
        "d_created_time": results[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "d_last_update": results[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "hardware_sn": results[4],
        "hardware_model": results[5],
        "nic_type": results[6],
        "nic_ipv4": results[7],
        "nic_mac": results[8],
        "wifi_mac": results[9],
        "LTE_IMEI": results[10],
        "software_version": results[13],
        "software_last_update": results[14].strftime('%Y-%m-%d %H:%M:%S'),
        "status": results[15],
    }
    return response.json(
        {
            "status": 1,
            "message": "获取设备成功",
            "data": [device]
        })


# 基于设备型号与序列号SN组合查询设备
async def handle_hardware_info(hardware_model, hardware_sn):
    # 处理hardware_model和hardware_sn的逻辑
    sql2 = "select * from device where hardware_model = %s and hardware_sn = %s and status != 2"
    value = (hardware_model, hardware_sn)
    try:
        results = SQLR.select_connection_one(sql2, value)
    except Exception as e:
        logger.error(f"Error in add_devices: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error adding device, group, and relation"
            }
        )
    if results is None:
        return response.json(
            {
                "status": 0,
                "message": "数据库没有对应数据"
            }
        )

    device = {
        "did": results[0],
            "dname": results[1],
            "d_created_time": results[2].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "d_last_update": results[3].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "hardware_sn": results[4],
            "hardware_model": results[5],
            "nic_type": results[6],
            "nic_ipv4": results[7],
            "nic_mac": results[8],
            "wifi_mac": results[9],
            "LTE_IMEI": results[10],
            "software_version": results[13],
            "software_last_update": results[14].strftime('%Y-%m-%d %H:%M:%S'),
            "status": results[15],
    }
    return response.json(
        {
            "status": 1,
            "message": "获取设备成功",
            "data": [device]
        })


# 查询所有设备基础信息
async def handle_no_params():
    sql3 = "select * from device where status != 2"
    try:
        results = SQLR.select_connection_all(sql3)
    except Exception as e:
        logger.error(f"Error in add_devices: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error adding device, group, and relation"
            }
        )
    if results is None:
        return response.json(
            {
                "status": 0,
                "message": "数据库没有对应数据"
            }
        )
    devices = []
    for row in results:
        device = {
            "did": row[0],
            "dname": row[1],
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
        }
        devices.append(device)
    return response.json(
        {
            "status": 1,
            "message": "获取设备成功",
            "data": devices
        })


async def get_devices(request):
    # print(request.args)
    did = request.args.get('did')
    hardware_model = request.args.get('hardware_model')
    hardware_sn = request.args.get('hardware_sn')

    # print(hardware_model)
    # print(hardware_sn)

    if did:
        return await handle_did(did)
    elif hardware_model and hardware_sn:
        return await handle_hardware_info(hardware_model, hardware_sn)
    elif len(request.args) == 0:
        return await handle_no_params()
    else:
        return response.json(
            {
                "status": 0,
                "message": "Error: 不合规范的url"
            },
            status=400  # Bad Request
        )
