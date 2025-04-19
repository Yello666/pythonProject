class send_PDU(object):
    def __init__(self,hardware_sn,did,method,type,data):
        # 硬件自带的序列号，标识唯一一个硬件
        self.hardware_sn = hardware_sn
        # 设备登录后获得did，有利于服务器标识唯一一个硬件
        self.did = did
        # 指令字段，说明是什么指令
        self.method = method
        # 标识PDU是框架内还是框架外
        self.type = type
        # 发送的数据
        self.data = data

# class recv_PDU(object):
#     def __init__(self,status,type,data):
#         # 请求是否成功的状态码
#         self.status = status
#         # 标识PDU是框架内还是框架外
#         self.type = type
#         # 返回的数据
#         self.data = data