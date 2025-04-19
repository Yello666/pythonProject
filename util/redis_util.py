import threading
from turtledemo.chaos import coosys

import redis
import uuid

# 存储redis连接的全局变量
connection_redis=None

# 开发环境(本地)的redis配置
redis_config = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
    'password': '123456',
}

# 用于初始化redis的时候控制并发
lock = threading.Lock()

# 将 redis_client 保存到全局变量中
async def init_redis_connect():
    global connection_redis
    if connection_redis is None:  # 第一次检查
        with lock:  # 获取锁
            if connection_redis is None:  # 第二次检查
                try:
                    redis_pool = redis.ConnectionPool(
                        host=redis_config['host'],
                        port=redis_config['port'],
                        db=redis_config['db'],
                        password=redis_config['password'],  # 配置密码
                        decode_responses=True,  # 自动解码为字符串
                    )
                    connection_redis = redis.Redis(connection_pool=redis_pool)
                except Exception as e:
                    print(f"Error initializing Redis connection: {e}")
                    raise

# 获取redis连接:
async def get_redis():
    global connection_redis
    if connection_redis is None:
        return None
    else:
        return connection_redis

# 通过全局变量关闭redis连接
async def close_redis_connect():
    redis_client = connection_redis
    if redis_client:
        redis_client.connection_pool.disconnect()


# 在redis中保存token并设置过期时间
# 如果redis中存在那么就只刷新时间
async def set_token_connection(key, ttl):
    if connection_redis.exists(key):
        connection_redis.expire(key, ttl)
    else:
        # 生成 token(uuid)生成
        token = uuid.uuid4().hex
        # 设置
        connection_redis.set(key, token, ex=ttl)

# 通过全局变量删除redis中token
async def delete_token_connection(key):
   connection_redis.delete(key)


#通过全局变量增加redis心跳次数
async def incr_retry_heartbeat_count_connection(key):
    connection_redis.incrby(key, 1)

# 通过全局变量获取redis中心跳次数
async def get_retry_heartbeat_count_connection(key):
    if not connection_redis.exists(key):
        return 0
    retry_count = connection_redis.get(key)
    return int(retry_count) if retry_count is not None else 0

#通过全局变量获取redis业务重试次数
async def incr_retry_job_count_connection(key):
    connection_redis.incrby(key, 1)

#通过全局变量获取redis中业务次数
async def get_retry_job_count_connection(key):
    retry_count = connection_redis.get(key)
    if retry_count is None:
        return 0
    return int(retry_count)

#通过全局变量查询redis中token是否存在
async def has_token_connection(key):
    return connection_redis.exists(key)

# 通过全局变量更新redis中的值
async def set_retry_heartbeat_count_connection(key,num):
    connection_redis.set(key, num)

# 查询key的过期时间
async def get_key_expire_time(key:str):
    return connection_redis.ttl(key)


# 通过全局变量设置job_token：
async def set_job_name_connection(key):
    # 生成 token(uuid)生成
    token = uuid.uuid4().hex
    # 设置
    connection_redis.set(key, token)