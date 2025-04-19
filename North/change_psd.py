from sanic import response
from util import mysql_util as SQLR
import hashlib
import random
import string
from sanic.log import logger


# 生成一个盐值
def generate_salt1(length=10):
    salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return salt


# 使用sha256散列函数进行加盐散列
def hash_password1(password, salt):
    m = hashlib.sha256()
    # 先放入盐值，再放入密码
    m.update(salt.encode())
    m.update(password.encode())
    # 返回16进制表示的散列值
    return m.hexdigest()


# 修改设备密码
async def change_psd(request):
    data = request.json
    did = data.get('did')  # 拿到设备的did和原密码和新密码，psd是一个列表，第一位是原密码，第二位是新密码
    psd = data.get('secret')
    old_psd = psd[0]
    new_psd = psd[1]

    if not did or not psd:
        return response.json(
            {
                "status": 0,
                "message": "Missing required parameters"
            },
            status=400  # Bad Request
        )
# 根据did找到之前的设备
    sql1 = "SELECT salt, secret FROM device WHERE did = %s and status != 2;"
    value1 = (did,)
    try:
        # 查询did对应设备的salt和secret
        results = SQLR.select_connection_one(sql1, value1)
    except Exception as e:
        # logger.error(f"Error in add_devices: {e}")
        # return response.json(
        #     {
        #         "status": 0,
        #         "message": "Error adding device, group, and relation"
        #     }
        # )
        logger.error(f"Error in change_psd: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error querying device salt and secret"
            }
        )
    if results is None:
        return response.json(
            {
                "status": 0,
                "message": "不存在该设备"
            }
        )
    # print(results)
    salt, secret = results
    device = {
        "salt": salt,
        "secret": secret
    }
    # 将密码与输入的密码做对比
    secret_o = hash_password1(old_psd, device['salt'])
    if secret_o != device['secret']:
        return response.json(
            {
                "status": 0,
                "message": "设备密码错误"
            }
        )
    salt_n = generate_salt1()
    secret_n = hash_password1(new_psd, salt_n)
    # 修改密码
    sql2 = "UPDATE device SET salt = %s, secret = %s WHERE did = %s and status != 2;"
    value2 = (salt_n, secret_n, did)
    try:
        results = SQLR.update_connection(sql2, value2)
    except Exception as e:
        # logger.error(f"Error in add_devices: {e}")
        # return response.json(
        #     {
        #         "status": 0,
        #         "message": "Error adding device, group, and relation"
        #     }
        # )
        logger.error(f"Error in change_psd: {e}")
        return response.json(
            {
                "status": 0,
                "message": "Error updating device password"
            }
        )
    return response.json(
        {
            "status": 1,
            "message": "密码更新成功"
        }
    )
