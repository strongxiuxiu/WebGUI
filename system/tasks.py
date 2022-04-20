# app文件夹的根目录下创建tasks.py，必须是这个名字，才能自动发现
# **app/tasks.py
# 引入celery实例
# 异步任务
import time

import datetime

from storage_web.celeryCenter import app as celeryApp
from django.core.cache import cache
from public_function import tool, web_conf
from public_function.redis_tool import RedisUtils
from public_function.storage_api import GetIP


# 创建一个任务
@celeryApp.task(acks_late=True)
def onefunction(item):
    pass
    print(item, 333)
    print(1111)
    # time.sleep(111)
    print(2)
    return 'ok'


# 定时任务
from storage_web.celeryCenter import app


def monitoring():
    # tool.Network().get_playback_network()
    # tool.CPU().get_playback_cpu()
    # tool.Memory().get_playback_memory()
    # tool.Disk().get_playback_io()
    # all_playback_dict = {}
    # all_playback_dict["network"] = tool.Network().get_playback_network()
    # all_playback_dict["cpu"] = tool.Memory().get_playback_memory()
    # all_playback_dict["memery"] = tool.Network().get_playback_network()
    # all_playback_dict["disk"] = tool.Disk().get_playback_io()
    # print(tool.Network().get_playback_network())
    # print(tool.CPU().get_playback_cpu())
    # print(tool.Memory().get_playback_memory())
    # print(tool.Disk().get_playback_io(),444555)
    thread_list = []
    res_name = ["network", "cpu_usage", "memory_usage", "IOPS"]
    network1 = tool.MyThread(tool.Network().get_playback_network)  # 网络测速
    cpu1 = tool.MyThread(tool.CPU().get_playback_cpu)  # cpu用量
    memory1 = tool.MyThread(tool.Memory().get_playback_memory)  # 内存使用率
    iops = tool.MyThread(tool.Disk().get_playback_io)  # 磁盘IO读写次数
    # network1.setDaemon()
    network1.start()
    thread_list.append(network1)
    cpu1.start()
    thread_list.append(cpu1)
    memory1.start()
    thread_list.append(memory1)
    iops.start()
    thread_list.append(iops)
    res_dict = {}
    for name, tr in zip(res_name, thread_list):
        tr.join()
        res_dict[name] = tr.get_result()  # 获取打印的数据值\
    print(res_dict, 33333)
    return res_dict


def test22():
    print("test22--------------")
    # test11()


@app.task
def celery_run():
    r = RedisUtils(host=GetIP.get_self_ip(), port=web_conf.redis_port, password=web_conf.redis_password,
                   db=web_conf.redis_db)

    r.set_key_value(int(time.time()), str(monitoring()), 60 * 60 * 12 * 2)  # 存了12小时的数据
    return "success"


if __name__ == '__main__':
    celery_run()
