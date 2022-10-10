import psutil
import speedtest
import time
from flask import current_app

def get_cpu_status():
    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    res = {
        'physicalCores':physical_cores,
        'logicalCores':logical_cores,
        'percentage':cpu_percent
    }
    return res

def get_memory_status():
    virtual_mem = psutil.virtual_memory()
    mem_total = mem_unit_format(virtual_mem.total)
    mem_used = mem_unit_format(virtual_mem.used)
    mem_free = mem_unit_format(virtual_mem.free + virtual_mem.buffers + virtual_mem.cached)
    mem_percent = virtual_mem.percent
    res={
        'total':mem_total,
        'used':mem_used,
        'free':mem_free,
        'percentage':mem_percent
    }
    current_app.logger.info("【get_memory_status】")
    current_app.logger.info(res)
    return res

def mem_unit_format(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E')
    prefix = {}
    for i, k in enumerate(symbols):
        prefix[k] = 1<< (i+1) * 10
    for k in reversed(symbols):
        if n >= prefix[k]:
            value = float(n) / prefix[k]
            return '%.1f%s' % (value, k)
    return '%sB' % n

# 测速
def get_test_speed():
    # 创建测试实例
    test = speedtest.Speedtest()
    # 获取可用于测试的服务器列表
    test.get_servers()
    # 筛选出最佳测试服务器
    bestTestServer = test.get_best_server()
    download_speed = str(round(test.download() / 1024 / 1024, 2)) + 'Mbps'
    upload_speed = str(round(test.upload() / 1024 / 1024, 2)) + 'Mbps'
    res={
        "downloadSpeed":download_speed,
        "uploadSpeed":upload_speed
    }
    res_str=str(res).replace("'", '"')
    return res_str

def get_realtime_speed():
    sent_before = psutil.net_io_counters().bytes_sent  # 已发送的流量
    recv_before = psutil.net_io_counters().bytes_recv  # 已接收的流量
    time.sleep(1)
    sent_now = psutil.net_io_counters().bytes_sent
    recv_now = psutil.net_io_counters().bytes_recv
    sent = (sent_now - sent_before)/1024
    recv = (recv_now - recv_before)/1024
    # print(time.strftime(" [%Y-%m-%d %H:%M:%S] ", time.localtime()))
    # print("上传：{0}KB/s".format("%.2f"%sent))
    # print("下载：{0}KB/s".format("%.2f"%recv))
    # print('-'*32)