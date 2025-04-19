# redis 常量类

# client端token的key前缀
client_heartbeat_token_key_prefix = 'device_manage:client:heartbeat:'
# client端心跳重试次数key前缀
client_heartbeat_retry_count_key_prefix = 'device_manage:client:heartbeat_retry:'
# client端状态数据上报的key前缀
client_status_data_upload_key_prefix = 'device_manage:client:status_upload:'

# server端token的key前缀
# 因为server端需要维护多个心跳token，所以这里只是前缀，完整的key: (server_heartbeat_token_key_prefix + 设备id)
server_heartbeat_token_key_prefix = 'device_manage:server:heartbeat:'
# server端业务重试次数key前缀
# 完整的key: (device_manage:server:job_retry + 设备id+job_name)
server_job_retry_count_key_prefix = 'device_manage:server:job_retry:'
# server端判断指令token的key
# 完整的key:(device_manage:server:job + 设备id + job_name)
server_job_token_key_prefix = 'device_manage:server:job:'
