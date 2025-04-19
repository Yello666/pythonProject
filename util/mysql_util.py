import pymysql
from sanic.log import logger
#部署到流水线的
# db_config = {
#     'host':'47.113.197.166',
#     'port':3306,
#     'user':'root',
#     'password':'Teamcode123',
#     'db': 'DeviceManage'
# }

#本地自己搞测试的
db_config = {
    'host':'localhost',
    'port':3306,
    'user':'test',
    'password':'123456',
    'db': 'device_manage'
}

# 插入数据的模板方法
# quere: sql
# values: sql中由占位符，所以values就是填充sql中占位符的属性
def insert_connection(quere, values):
    try:
        #建立连接
        connection = pymysql.connect(**db_config)
        print("数据库连接成功")
        connection.cursor().execute(quere,values)
        connection.commit()
    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")

# 查询所有数据的模板方法
# quere: sql
def select_connection_all(quere):
    try:
        connection = pymysql.connect(**db_config)
        print("数据库连接成功")
        cursor = connection.cursor()
        cursor.execute(quere)
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")

# 查询单条数据的模板方法
# quere: sql
# values: sql中由占位符，所以values就是填充sql中占位符的属性
def select_connection_one(quere, value):
    try:
        connection = pymysql.connect(**db_config)
        print("数据库连接成功")
        cursor = connection.cursor()
        cursor.execute(quere,value)
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")

# 查询所有数据的模板方法
# quere: sql
# values: sql中由占位符，所以values就是填充sql中占位符的属性
def select_connection_all1(quere, value):
    try:
        connection = pymysql.connect(**db_config)
        print("数据库连接成功")
        cursor = connection.cursor()
        cursor.execute(quere,value)
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")

# 删除数据的模板方法
# quere: sql
# values: sql中由占位符，所以values就是填充sql中占位符的属性
def delete_connection(quere, values):
    try:
        connection = pymysql.connect(**db_config)
        print("数据库连接成功")
        connection.cursor().execute(quere,values)
        connection.commit()
    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")

# 修改数据的模板方法
# quere: sql
# values: sql中由占位符，所以values就是填充sql中占位符的属性
def update_connection(quere, values):
    try:
        connection = pymysql.connect(**db_config)
        print("数据库连接成功")
        connection.cursor().execute(quere,values)
        connection.commit()
    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")

# 查询数据是否存在的模板方法
# quere: sql
# values: sql中由占位符，所以values就是填充sql中占位符的属性
def is_exist(query, values):
    try:
        connection = pymysql.connect(**db_config)
        print("数据库连接成功")
        cursor = connection.cursor()
        cursor.execute(query, values)
        result = cursor.fetchone()  # 获取查询结果
        connection.close()  # 关闭数据库连接
        if result:
            return True  # 如果结果不为空，表示did存在
        else:
            return False  # 如果结果为空，表示did不存在
    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")
        return False  # 处理数据库连接或查询错误情况     
        
# 返回由hardware_sn与加盐密码组成的键值对构成的字典
def export_sn_password():
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT hardware_sn, secret FROM device where status != 2;"
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 构建字典
        serial_number_password_dict = {}
        for result in results:
            serial_number = result[0]
            password = result[1]
            serial_number_password_dict[serial_number] = password
        
        return serial_number_password_dict
    
    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")
        return False 
        
# 由hardware_sn返回该行对应盐值
def get_salt_by_sn(hardware_sn):
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        query = f"SELECT salt FROM device WHERE hardware_sn = '{hardware_sn}' and status != 2;"
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            salt_value = result[0]
            return salt_value
        else:
            return ''
    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")
        return False  

# 由hardware_sn返回该设备对应状态
def get_status_by_sn(hardware_sn):
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        query = f"SELECT status FROM device WHERE hardware_sn = '{hardware_sn}' and status != 2;"
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            status_value = result[0]
            return status_value

    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")
        return False

# 根据 hardware_sn 获取设备信息
def get_info_by_sn(hardware_sn):
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        query = f"SELECT * FROM device WHERE hardware_sn = '{hardware_sn}' and status != 2;"
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            # 获取列名
            field_names = [desc[0] for desc in cursor.description]
            # 将结果转为字典
            return dict(zip(field_names, result))

    except Exception as e:
        logger.error(f"数据库连接失败，错误信息为：{e}")
        return None

if __name__ == "__main__":
    select_connection_all("select * from device where status != 2;")
