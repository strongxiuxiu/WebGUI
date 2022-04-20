import psutil
import time
import threading

from public_function.storage_api import RequestApi, GetIP
from public_function import web_conf


class MyThread(threading.Thread):

    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None


class SystemResources:
    """
        这是一个系统资源的整合类，包含所有的系统资源信息，
        包括CPU,硬盘，内存，进程，网络资源
    """

    def __init__(self, ip=None):
        """
            cpu_freq([percpu])：返回cpu频率
            psutil.pids()	以列表的形式返回当前正在运行的进程
            psutil.pid_exists(1)	判断给点定的pid是否存在
            psutil.process_iter()	迭代当前正在运行的进程，返回的是每个进程的Process对象
            psutil.Process()	对进程进行封装，可以使用该类的方法获取进行的详细信息，或者给进程发送信号。
            psutil.net_io_counter([pernic])	以命名元组的形式返回当前系统中每块网卡的网络io统计信息，包括收发字节数，收发包的数量、出错的情况和删包情况。当pernic为True时，则列出所有网卡的统计信息。
            psutil.net_connections([kind])	以列表的形式返回每个网络连接的详细信息(namedtuple)。命名元组包含fd, family, type, laddr, raddr, status, pid等信息。kind表示过滤的连接类型，支持的值如下：(默认为inet)
            psutil.net_if_addrs()	以字典的形式返回网卡的配置信息，包括IP地址和mac地址、子网掩码和广播地址。
            psutil.net_if_stats()	返回网卡的详细信息，包括是否启动、通信类型、传输速度与mtu。
            psutil.users()	以命名元组的方式返回当前登陆用户的信息，包括用户名，登陆时间，终端，与主机信息
            psutil.boot_time()	以时间戳的形式返回系统的启动时间
            psutil.disk_io_counters()	disk_io_counters([perdisk])：以命名元组的形式返回磁盘io统计信息(汇总的)，包括读、写的次数，读、写的字节数等。
            当perdisk的值为True，则分别列出单个磁盘的统计信息(字典：key为磁盘名称，value为统计的namedtuple)。
            psutil.disk_partitions()	disk_partitions([all=False])：以命名元组的形式返回所有已挂载的磁盘，包含磁盘名称，挂载点，文件系统类型等信息。
            当all等于True时，返回包含/proc等特殊文件系统的挂载信息
            psutil.disk_usage()	disk_usage(path)：以命名元组的形式返回path所在磁盘的使用情况，包括磁盘的容量、已经使用的磁盘容量、磁盘的空间利用率等。
                    psutil.cpu_count()	cpu_count(,[logical]):默认返回逻辑CPU的个数,当设置logical的参数为False时，返回物理CPU的个数。
            psutil.cpu_percent()	cpu_percent(,[percpu],[interval])：返回CPU的利用率,percpu为True时显示所有物理核心的利用率,interval不为0时,则阻塞时显示interval执行的时间内的平均利用率
            psutil.cpu_times()	cpu_times(,[percpu])：以命名元组(namedtuple)的形式返回cpu的时间花费,percpu=True表示获取每个CPU的时间花费
            psutil.cpu_times_percent()	cpu_times_percent(,[percpu])：功能和cpu_times大致相同，看字面意思就能知道，该函数返回的是耗时比例。
            psutil.cpu_stats()	cpu_stats()以命名元组的形式返回CPU的统计信息，包括上下文切换，中断，软中断和系统调用次数。
            psutil.cpu_freq()	cpu_freq([percpu])：返回cpu频率
        """
        self.memory = psutil.virtual_memory()
        self.percent = psutil.cpu_percent()
        self.usage = psutil.disk_usage('/')
        self.counters = psutil.net_io_counters()
        self.pid = psutil.pids()
        # self.ip = ip
        self.ip = GetIP.get_self_ip()

    def __repr__(self):
        """
            打印一份改系统当前设备的信息，如包含内存，cpu,硬盘,网络，进程等
        """
        return '<ip地址为:{},memory==>{},cpu==>{},disk==>{},network==>{},pid==>{}>'.format(
            self.ip,
            self.memory,
            self.percent,
            self.usage,
            self.counters,
            self.pid
        )

    def get_cpu(self):
        """ 获取cpu信息"""
        pass

    def get_memory(self):
        """ 获取内存信息"""
        pass

    def get_disk(self):
        """ 获取硬盘信息"""
        pass

    def get_network(self):
        """ 获取网络信息"""
        pass

    def get_pid(self):
        """ 获取进程信息"""
        pass

    def result(self):
        """ 返回数据信息"""
        pass


class SystemCPU(SystemResources):
    """
        包含逻辑CPU的个数，pu的时间花费，CPU的利用率，CPU的统计信息，cpu频率
    """

    def __init__(self, *args, **kwargs):
        """
            这个类是包含系统所有的CPU信息资源，继承了基础的SystemResources类
        """
        super().__init__(*args, **kwargs)
        self.args = args
        self.cpu_dict = {}

    def __del__(self):
        return True

    def cpu_count(self):
        """
        cpu_count()	cpu_count(,[logical]):默认返回逻辑CPU的个数,当设置logical的参数为False时，返回物理CPU的个数。
        """
        return psutil.cpu_count()

    def cpu_percent(self, interval=1):
        """
        cpu_percent()	cpu_percent(,[percpu],[interval])：返回CPU的利用率,percpu为True时显示所有物理核心的利用率,interval不为0时,则阻塞时显示interval执行的时间内的平均利用率
        """
        # print(psutil.cpu_percent(),555555)
        return psutil.cpu_percent(interval=interval)

    def cpu_times(self):
        """
        cpu_times()	cpu_times(,[percpu])：以命名元组(namedtuple)的形式返回cpu的时间花费,percpu=True表示获取每个CPU的时间花费
        """
        return psutil.cpu_times()

    def cpu_times_percent(self):
        """
        cpu_times_percent()	cpu_times_percent(,[percpu])：功能和cpu_times大致相同，看字面意思就能知道，该函数返回的是耗时比例。
        """
        return psutil.cpu_times_percent()

    def cpu_stats(self):
        """
        cpu_stats()	cpu_stats()以命名元组的形式返回CPU的统计信息，包括上下文切换，中断，软中断和系统调用次数。
        """
        return psutil.cpu_stats()

    def cpu_freq(self):
        """
        cpu_freq()	cpu_freq([percpu])：返回cpu频率
        """
        return psutil.cpu_freq()

    def result(self):
        """
            返回数据汇总的json数据
        """
        self.cpu_dict['cpu_freq'] = self.cpu_freq()
        self.cpu_dict['cpu_count'] = self.cpu_count()
        self.cpu_dict['cpu_percent'] = self.cpu_percent
        self.cpu_dict['cpu_times'] = self.cpu_times()
        self.cpu_dict['cpu_times_percent'] = self.cpu_times_percent
        self.cpu_dict['cpu_stats'] = self.cpu_stats()
        return self.cpu_dict


class SystemMemory(SystemResources):
    """
        包含总内存，可用内存，内存利用率,swap/memory使用情况
    """

    def __init__(self, data=None, *args, **kwargs):
        """
            这个类是包含系统所有的Memory信息资源，继承了基础的SystemResources类
        """
        super().__init__(*args, **kwargs)
        self.data = data
        self.memory_dict = {}

    def __del__(self):
        return True

    def virtual_memory(self):
        """
        virtual_memory()：以命名元组的形式返回内存使用情况，包括总内存，可用内存，内存利用率，buffer和cache等。单位为字节。
        #total:总物理内存
        #available:可用的内存
        #used:使用的内存
        #free：完全没有使用的内存
        #active：当前正在使用的内存
        #inactive：标记为未使用的内存
        #buffers：缓存文件系统元数据使用的内存
        #cached:缓存各种文件的内存
        #shared:可以被多个进程同时访问的内存
        #slab:内核数据结构缓存的内存
        # percent
        """
        return psutil.virtual_memory()

    def swap_memory(self):
        """
        swap_memory()：以命名元组的形式返回swap/memory使用情况，包含swap中页的换入和换出
        """
        return psutil.swap_memory()

    def result(self):
        """
            汇总一份系统所有的内存信息,以dict形式返回
        """
        self.memory_dict['virtual_memory'] = self.virtual_memory()
        self.memory_dict['swap_memory'] = self.swap_memory()
        return self.memory_dict


class SystemDisk(SystemResources):
    """
        包含磁盘io统计信息(汇总的)，包括读、写的次数，读、写的字节数等。
        磁盘名称，挂载点，文件系统类型,磁盘的容量、
        已经使用的磁盘容量、磁盘的空间利用率
    """

    def __init__(self, data=None, *args, **kwargs):
        """
            这个类是包含系统所有的CPU信息资源，继承了基础的SystemResources类
        """
        super().__init__(*args, **kwargs)
        self.data = data
        self.path = '/'
        self.disk_dict = {}
        self.disk_usage_dict = {}

    def __del__(self):
        return True

    def disk_io_counters(self):
        """
        disk_io_counters([perdisk])：以命名元组的形式返回磁盘io统计信息(汇总的)，包括读、写的次数，读、写的字节数等。
        当perdisk的值为True，则分别列出单个磁盘的统计信息(字典：key为磁盘名称，value为统计的namedtuple)。
        """
        return psutil.disk_io_counters(perdisk=True)

    def disk_partitions(self):
        """
        disk_partitions([all=False])：以命名元组的形式返回所有已挂载的磁盘，包含磁盘名称，挂载点，文件系统类型等信息。
        当all等于True时，返回包含/proc等特殊文件系统的挂载信息
        """
        return psutil.disk_partitions()

    def disk_usage(self, path=None):
        """
        disk_usage(path)：以命名元组的形式返回path所在磁盘的使用情况，包括磁盘的容量、已经使用的磁盘容量、磁盘的空间利用率等。
        """
        if path:
            self.path = path
        res = psutil.disk_usage(self.path)
        self.disk_usage_dict["total"] = res.total
        self.disk_usage_dict["used"] = res.used
        self.disk_usage_dict["free"] = res.free
        self.disk_usage_dict["percent"] = res.percent
        return self.disk_usage_dict

    def result(self):
        """
            汇总一份系统所有的硬盘信息,以dict形式返回
        """
        self.disk_dict["disk_io_counters"] = self.disk_io_counters()
        self.disk_dict["disk_partitions"] = self.disk_partitions()
        self.disk_dict["disk_usage"] = self.disk_usage(self.path)
        return self.disk_dict


class SystemNetwork(SystemResources):
    """
        包含磁盘io统计信息(汇总的)，包括读、写的次数，读、写的字节数等。
        磁盘名称，挂载点，文件系统类型,磁盘的容量、
        已经使用的磁盘容量、磁盘的空间利用率
    """

    def __init__(self, data=None, *args, **kwargs):
        """
            这个类是包含系统所有的网络资源，继承了基础的SystemResources类
        """
        super().__init__(*args, **kwargs)
        self.data = data
        self.network_dict = {}

    def __del__(self):
        return True

    def net_io_counters(self, pernic=True):
        """
        psutil.net_io_counter([pernic])
        以命名元组的形式返回当前系统中每块网卡的网络io统计信息，包括收发字节数，收发包的数量、
        出错的情况和删包情况。
        当pernic为True时，则列出所有网卡的统计信息。
        """
        return psutil.net_io_counters(pernic=pernic)

    def net_connections(self):
        """
        psutil.net_connections([kind])
        以列表的形式返回每个网络连接的详细信息(namedtuple)。
        命名元组包含fd, family, type, laddr, raddr, status, pid等信息。
        kind表示过滤的连接类型，支持的值如下：(默认为inet)
        """
        return psutil.net_connections()

    def net_if_addrs(self):
        """
        psutil.net_if_addrs()
        以字典的形式返回网卡的配置信息，包括IP地址和mac地址、子网掩码和广播地址。
        """
        return psutil.net_if_addrs()

    def net_if_stats(self):
        """
        psutil.net_if_stats()
        返回网卡的详细信息，包括是否启动、通信类型、传输速度与mtu。
        """
        return psutil.net_if_stats()

    def users(self):
        """
        psutil.users()
        以命名元组的方式返回当前登陆用户的信息，包括用户名，登陆时间，终端，与主机信息
        """
        return psutil.users()

    def boot_time(self):
        """
        psutil.boot_time()
        以时间戳的形式返回系统的启动时间
        """
        return psutil.boot_time()

    def result(self):
        """
            汇总一份系统所有的网络信息,以dict形式返回
        """
        self.network_dict["net_io_counter"] = self.net_io_counters()
        self.network_dict["net_connections"] = self.net_connections()
        self.network_dict["net_if_addrs"] = self.net_if_addrs()
        self.network_dict["net_if_stats"] = self.net_if_stats()
        self.network_dict["users"] = self.users()
        self.network_dict["boot_time"] = self.boot_time()
        return self.network_dict


class SystemPid(SystemResources):
    """
        包含磁盘io统计信息(汇总的)，包括读、写的次数，读、写的字节数等。
        磁盘名称，挂载点，文件系统类型,磁盘的容量、
        已经使用的磁盘容量、磁盘的空间利用率
    """

    def __init__(self, data=None, *args, **kwargs):
        """
            这个类是包含系统所有的CPU信息资源，继承了基础的SystemResources类
        """
        super().__init__(*args, **kwargs)
        self.data = data
        self.pid = 1
        self.pid_dict = {}

    def __del__(self):
        return True

    def pids(self):
        """
        psutil.pids()以列表的形式返回当前正在运行的进程
        """
        return psutil.pids()

    def pid_exists(self, pid=None):
        """
        psutil.pid_exists(1)	判断给点定的pid是否存在
        """
        if pid:
            return psutil.pid_exists(pid)
        else:
            return psutil.pid_exists(self.pid)

    def process_iter(self):
        """
        psutil.process_iter()	迭代当前正在运行的进程，返回的是每个进程的Process对象
        """
        return psutil.process_iter()

    def Process(self):
        """
        psutil.Process()	对进程进行封装，可以使用该类的方法获取进行的详细信息，或者给进程发送信号。
        """
        return psutil.Process()

    def result(self):
        """
            汇总一份系统所有的进程信息,以dict形式返回
        """
        self.pid_dict["pids"] = self.pids()
        self.pid_dict["pid_exists"] = self.pid_exists()
        self.pid_dict["process_iter"] = self.process_iter()
        self.pid_dict["Process"] = self.Process()
        return self.pid_dict


class Network(SystemNetwork):
    def __init__(self, *args, **kwargs):
        """
            这个类是用来操作实际的网络相关操作，继承了基础的SystemNetwork类
        """
        super().__init__(*args, **kwargs)

    def __del__(self):
        return True

    def get_all_network_card(self):
        """
            获取所有网卡名称
        """

        return self.net_io_counters().keys()

    def get_network_rate(self, nc_name=None):
        """
            可以获取单个或者所有网卡速率
            返回示例
            [{'nt_card': 'ens37', 'input': '0.76171875KB/S', 'Output': '0.76171875KB/S'},
             {'nt_card': 'lo', 'input': '0.1015625KB/S', 'Output': '0.1015625KB/S'},
             {'nt_card': 'ens33', 'input': '0.8203125KB/S', 'Output': '0.8203125KB/S'},
             {'nt_card': 'ens38', 'input': '0.76171875KB/S', 'Output': '0.76171875KB/S'}]
        """
        all_network_rate = []
        key_info, net_in, net_out = self.get_rate(self.get_key)
        for key in key_info:
            if nc_name:
                if nc_name == key:
                    rate = {}
                    rate["nt_card"] = key
                    rate["input"] = "{}KB/S".format(net_in.get(key))
                    rate["Output"] = "{}KB/S".format(net_in.get(key))
                    all_network_rate.append(rate)
            else:
                rate = {}
                rate["nt_card"] = key
                rate["input"] = "{}KB/S".format(net_in.get(key))
                rate["Output"] = "{}KB/S".format(net_in.get(key))
                all_network_rate.append(rate)
        return all_network_rate

    def get_a_network_rate(self, nc_name):
        """
            获取单个网卡速率
            ncname = 网卡名称
        """
        pass

    def get_key(self):
        recv = {}
        sent = {}
        key_info = self.net_io_counters()  # 获取网卡名称
        for key in key_info:
            recv.setdefault(key, self.net_io_counters().get(key).bytes_recv)  # 各网卡接收的字节数
            sent.setdefault(key, self.net_io_counters().get(key).bytes_sent)  # 各网卡发送的字节数

        return key_info, recv, sent

    def get_rate(self, func):

        key_info, old_recv, old_sent = func()  # 上一秒收集的数据
        # #
        time.sleep(1)

        key_info, now_recv, now_sent = func()  # 当前所收集的数据

        net_in = {}
        net_out = {}

        for key in key_info:
            net_in.setdefault(key, (now_recv.get(key) - old_recv.get(key)) / 1024)  # 每秒接收速率
            net_out.setdefault(key, (now_sent.get(key) - old_sent.get(key)) / 1024)  # 每秒发送速率

        return key_info, net_in, net_out

    def get_glances_cpu_info(self):
        """
            从glances里获取cpu的全部信息
        """
        api = RequestApi(ip=self.ip, url="/api/3/network", item=web_conf.default_monitoring_port)
        print(api.joint_url())  #
        res = api.get_public_api()

        return res


class CPU(SystemCPU):
    def __init__(self, *args, **kwargs):
        """
            这个类是用来操作实际的CPU相关操作，继承了基础的SystemCPU类
        """
        super().__init__(*args, **kwargs)

    def __del__(self):
        return True

    def get_usage_rate(self):
        """
            获取CPU的使用率
        """

        return self.cpu_percent(interval=1)

    def get_core_count(self):
        """
            获取CPU的核数
        """
        return self.cpu_count()

    def get_glances_cpu_info(self):
        """
            从glances里获取cpu的全部信息
        """
        api = RequestApi(ip=self.ip, url="/api/3/cpu", item=web_conf.default_monitoring_port)
        print(api.joint_url())
        res = api.get_public_api()

        return res


class Memory(SystemMemory):
    def __init__(self, *args, **kwargs):
        """
            这个类是用来操作实际的内存相关操作，继承了基础的SystemMemory类
        """
        super().__init__(*args, **kwargs)

    def __del__(self):
        return True

    def get_used_memory(self):
        """
            获取总内存，可用内存，内存利用率，buffer和cache等。单位为字节。
        """
        memory_info = self.virtual_memory()
        # "{}%".format(memory_info.percent)
        return memory_info.percent

    def get(self):
        """

        """
        pass


class Disk(SystemDisk):
    def __init__(self, *args, **kwargs):
        """
            这个类是用来操作实际的内存相关操作，继承了基础的SystemMemory类
        """
        super().__init__(*args, **kwargs)

    def __del__(self):
        return True

    def get_disk_io(self):
        disk_info = []
        for k, v in self.disk_io_counters().items():
            disk_info_dict = {}
            disk_info_dict["disk_name"] = k
            disk_info_dict["read_merged_count"] = v.read_merged_count
            disk_info_dict["write_merged_count"] = v.write_merged_count
            disk_info_dict['unit'] = '次'
            disk_info.append(disk_info_dict)
        return disk_info

    def get(self):
        """

        """
        pass


# coding=utf-8
import threading
import time


def myFunc():
    time.sleep(5)
    print("myFunc执行了")


import pandas as pd

import datetime


def split_time_ranges(from_time, to_time, frequency):
    from_time, to_time = pd.to_datetime(from_time), pd.to_datetime(to_time)
    time_range = list(pd.date_range(from_time, to_time, freq='%sS' % frequency))
    if to_time not in time_range:
        time_range.append(to_time)
    time_range = [item.strftime("%Y-%m-%d %H:%M:%S") for item in time_range]
    time_ranges = []
    for item in time_range:
        f_time = item
        t_time = (datetime.datetime.strptime(item, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=frequency))
        if t_time >= to_time:
            t_time = to_time.strftime("%Y-%m-%d %H:%M:%S")
            time_ranges.append(f_time)
            break
        time_ranges.append(f_time)
    return time_ranges


if __name__ == '__main__':

    a = [{'network': {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125,
                      'ens37_output': 0.64453125, 'lo_input': 363.166015625, 'lo_output': 363.166015625,
                      'ens33_input': 3.818359375, 'ens33_output': 3.818359375, 'ens38_input': 0.64453125,
                      'ens38_output': 0.64453125}, 'cpu_usage': 21.2, 'memory_usage': 90.8,
          'IOPS': [{'sda_read': 164, 'sda_write': 20811}, {'sda1_read': 0, 'sda1_write': 0},
                   {'sda2_read': 164, 'sda2_write': 20811}, {'sr0_read': 0, 'sr0_write': 0},
                   {'dm-0_read': 0, 'dm-0_write': 0}, {'dm-1_read': 0, 'dm-1_write': 0}]},

         {'network': {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125,
                      'ens37_output': 0.64453125, 'lo_input': 363.166015625, 'lo_output': 363.166015625,
                      'ens33_input': 3.818359375, 'ens33_output': 3.818359375, 'ens38_input': 0.64453125,
                      'ens38_output': 0.64453125}, 'cpu_usage': 21.2, 'memory_usage': 90.8,
          'IOPS': [{'sda_read': 164, 'sda_write': 20811}, {'sda1_read': 0, 'sda1_write': 0},
                   {'sda2_read': 164, 'sda2_write': 20811}, {'sr0_read': 0, 'sr0_write': 0},
                   {'dm-0_read': 0, 'dm-0_write': 0}, {'dm-1_read': 0, 'dm-1_write': 0}]}, ]
    # receive_nt_card_name = False
    # nt_card_name_list = []
    # for i in a:
    #     print(i)
    #     # print(i)pr
    #     # print(1111111111111111111111)
    #     # if not receive_nt_card_name:  # 把所有网卡拿到哦
    #     #     for n in i["network"]:  #
    #     #         receive_nt_card_name = True
    #     #         nt_card_name_list.append(n["nt_card"])
    #     # print(nt_card_name_list)
    #     # for n in i["network"]:
    #     #
    #     #     # crad_name = str(n["nt_card"])
    #     #     # crad_name = []
    #     #     print(n)
    #     #     print(n["nt_card"])
    #     #     # print(crad_name)
    network = {}
    memory_usage = {}
    cpu_usage = {}
    cpu_data = []
    memory_data = []
    IOPS = {}
    network_data = []
    for i in a:
        t = datetime.datetime.now()
        cpu_usage_list = []
        cpu_usage_list.append(t)
        cpu_usage_list.append(i['cpu_usage'])
        cpu_data.append(cpu_usage_list)

        memory_usage_list = []
        memory_usage_list.append(t)
        memory_usage_list.append(i['memory_usage'])
        memory_data.append(memory_usage_list)

        print(i["network"])
        nt_name = False
        network_name_list = []
        for nt in i["network"]:
            if not nt_name:
                network_name_list.append(nt)
        # print(network_name_list)
        network_dict = {}
        network_a_all_list = []
        for nnl in network_name_list:
            for nt, nt_values in i["network"].items():
                if nnl == nt:
                    network_dict_a = {}
                    network_info_list = []
                    network_info_list.append(t)
                    network_info_list.append(nt_values)
                    network_dict_a[nnl] = network_info_list
                    network_a_all_list.append(network_dict_a)
            print(network_a_all_list,777777777777)
            # network_dict[nnl] = network_a_all_list
        # print(network_dict,4444)
        network_data.append(network_dict)
    print(network_data)
        # print(network_a_all_list)
        # network_dict["data"] = network_a_all_list
        # network_dict["unit"] = "KB/S"
        # network_dict["nt_card"] = nnl
    # print(network_dict, 66)
    # print(i)
    # network_list = []

    # IOPS_list = []
    # =============================

    # # =============================
    # for n in i["network"]:
    #
    #     network_list.append(t, i['memory_usage'])

    cpu_usage["cpu_usage"] = cpu_data
    memory_usage["memory_usage"] = memory_data
    # print(cpu_usage)
    # print(memory_usage,)
    # print(i)
    # timeStamp = 1637112478000
    #
    # dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
    # otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    # print(otherStyleTime)
    # start_time = 1637069278
    # end_time = 1637112478
    # timeArray = time.localtime(start_time)
    # from_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # # print(otherStyleTime)
    # timeArray = time.localtime(end_time)
    # to_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # frequency = end_time -start_time
    # print(frequency,333)
    # # timeArray = time.localtime(timeStamp)
    # # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # print(from_time,to_time,3333)
    # # print(otherStyleTime,33)
    # from_time = '2021-11-16 21:27:58'
    # to_time = '2021-11-17 09:27:58'
    import math
    from_time = "2021-11-17 18:04:11 "
    to_time = "2021-11-17 18:20:51"
    # print(timeStamp,3333)
    frequency = 12 * 60 * 60 / 3600
    frequency = 7300 / 3600

    print(math.ceil(frequency))
    print(frequency)
    print(frequency,4444444)
    # frequency = frequency / 3600
    time_ranges = split_time_ranges(from_time, to_time, frequency)
    print(time_ranges,3333)
    print(len(time_ranges),4444)
        # for i in time_ranges:
    #     print(i[0])
    # print(time_ranges,4444)
    # print(len(time_ranges))
    # t = threading.Thread(target=myFunc)
    # t.setDaemon(True)
    # t.start()
    #
    # t.join(3)
    # print("it's over")
    # 显示结果：　　myFunc执行了　　it
    # 's over可以看出，子线程结束时，用时1秒，没有超过主线程设定的3秒，所以主线程与子线程都被执行了

    print(1, 2)
    a = "1"
    v = "4"
    cv = a & v
    print(cv)
    print(Network().get_glances_cpu_info(), 5656)
    # print(CPU().get_glances_cpu_info())
    # print(Disk().get_disk_io())
    # for k, v in Disk().get_disk_io().items():
    #     print(k, v.read_merged_count, v.write_merged_count)
    # # [2, 5]
    print(Disk().get_disk_io())
    print(CPU().get_core_count())
    print(Memory().get_used_memory())
    print(Network().net_io_counters())
    for k, v in Network().net_io_counters().items():
        print(k, v)
    import threading
    import time


    class MyThread(threading.Thread):

        def __init__(self, func, args=()):
            super(MyThread, self).__init__()
            self.func = func
            self.args = args

        def run(self):
            self.result = self.func(*self.args)

        def get_result(self):
            try:
                return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
            except Exception:
                return None


    li = []
    Network_1 = MyThread(Network().get_network_rate)
    cpu_1 = MyThread(CPU().get_usage_rate)
    li.append(Network_1)
    li.append(cpu_1)
    Network_1.start()
    cpu_1.start()

    for t in li:
        t.join()  # 一定要join，不然主线程比子线程跑的快，会拿不到结果
        print(t.get_result())

    print(1111)
    # print(Network().get_network_rate())
    # print(CPU().get_usage_rate())
    #     print(i)
    # print(SystemCPU().result())
    # print(SystemPid().result())
    # print(SystemDisk().result())
    # print(SystemMemory().result())
    # print(SystemNetwork().result())
    # print(SystemNetwork().net_io_counters)
    # print(SystemNetwork().net_io_counters(pernic=True).keys())
    # a = SystemNetwork().net_io_counters().keys()

    # print(type(a))
    # for k,v in SystemNetwork().net_io_counters().key():
    #     print(k,v)
