from datetime import datetime

from sanic import response
from snowflake import SnowflakeGenerator
from sanic.log import logger
from util import mysql_util as SQLR
import time

gen = SnowflakeGenerator(2)  # 使用不同的机器ID生成不同的ID ; 2 是 machine_id
# 生成的ID是一个64位的整数，结构如下：时间戳部分（41位）,数据中心ID部分（5位）,机器ID部分（5位）,序列号部分（12位）


#处理添加设备组的请求
async def add_groups(request):
    data = request.json

    # 生成设备组信息
    # 雪花算法生成id
    gid = next(gen)  #从生成器中获取下一个值
    # 分组名称
    gname = data.get('group_name')
    # 创建时间时间戳
    curTime = time.time()
    g_created_time = datetime.fromtimestamp(curTime)
    # 修改时间时间戳
    g_last_update = datetime.fromtimestamp(curTime)

    values = (gid, gname, g_created_time, g_last_update, 0)

    # 构建 SQL 语句
    sql = """INSERT INTO device_group(gid, gname, g_created_time, g_last_update,g_status) VALUES (%s, %s, %s, %s, %s);"""

    try:
        # 执行插入操作
        SQLR.insert_connection(sql, values)

    except Exception as e:
        logger.error(f"Error in add_group: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error adding device group"
            }
        )

    print(f"数据已添加，group_gid为{gid}")
    return response.json(
        {
            "status": 200,
            "gid": gid,
            "message": f"添加成功,返回gid为{gid}"
        }
    )
