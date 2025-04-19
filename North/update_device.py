from sanic import response
from sanic.log import logger
from util import mysql_util as SQLR
from datetime import datetime


async def update_devices(request):
    data = request.json

    did = data.get('did')
    if not did:
        return response.json(
            {
                "status": 0,
                "message": "Error: 'did' is required for updating device information"
            },
            status=400  # Bad Request
        )

    # 查询设备是否存在
    check_device_query = "SELECT * FROM device WHERE did = %s and status != 2"
    check_device_values = (did,)
    existing_device = SQLR.select_connection_one(check_device_query, check_device_values)

    if not existing_device:
        return response.json(
            {
                "status": 0,
                "message": f"Error: Device with did {did} not found"
            },
            status=404  # Not Found
        )

    # 构建更新语句
    update_query = """
        UPDATE device 
        SET dname=%s, d_last_update=%s, hardware_sn=%s, hardware_model=%s,
            nic_type=%s, nic_mac=%s, nic_ipv4=%s,device.wifi_mac=%s,
            lte_imei=%s, software_version=%s, software_last_update=%s, status=%s
        WHERE did=%s and status != 2
    """

    # 获取新的设备信息
    # 如果没有获取到则选取existing_device[i]作为设备信息
    dname = data.get('dname', existing_device[1])
    d_last_update = int(datetime.now().timestamp() * 1000)
    hardware_sn = data.get('hardware_sn', existing_device[4])
    hardware_model = data.get('hardware_model', existing_device[5])
    nic_type = data.get('nic_type', existing_device[6])
    nic_ipv4 = data.get('nic_ipv4', existing_device[7])
    nic_mac = data.get('nic_mac', existing_device[8])
    wifi_mac = data.get('wifi_mac', existing_device[9])
    LTE_IMEI = data.get('LTE_IMEI', existing_device[10])
    status = data.get('status', existing_device[15])

    if existing_device[14] != data.get('software_version') and data.get('software_version') is not None:
        software_version = data.get('software_version')
        software_last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        software_version = existing_device[14]
        software_last_update = existing_device[15]

    update_values = (
        dname, d_last_update, hardware_sn, hardware_model,
        nic_type, nic_mac, nic_ipv4, wifi_mac,
        LTE_IMEI, software_version, software_last_update, status, did
    )

    try:
        # 执行更新操作
        SQLR.update_connection(update_query, update_values)

        return response.json(
            {
                "status": 1,
                "message": "Device information updated successfully"
            }
        )
    except Exception as e:
        logger.error(f"Error in update_devices: {e}")
        return response.json(
            {
                "status": 0,
                "message": f"Error updating device information: {e}"
            },
            status=500  # Internal Server Error
        )
