import random
import json
import psutil
import time
import threading
import multiprocessing

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from public_function import web_conf
from public_function.storage_api import RequestApi, GetIP


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


class ValidCodeImg:
    def __init__(self, width=120, height=40, code_count=4, font_size=32, point_count=10, line_count=2,
                 img_format='png'):
        '''
        可以生成一个经过降噪后的随机验证码的图片
        :param width: 图片宽度 单位px
        :param height: 图片高度 单位px
        :param code_count: 验证码个数
        :param font_size: 字体大小
        :param point_count: 噪点个数
        :param line_count: 划线个数
        :param img_format: 图片格式
        :return 生成的图片的bytes类型的data
        '''
        self.width = width
        self.height = height
        self.code_count = code_count
        self.font_size = font_size
        self.point_count = point_count
        self.line_count = line_count
        self.img_format = img_format

    @staticmethod
    def getRandomColor():
        '''获取一个随机颜色(r,g,b)格式的'''
        c1 = random.randint(0, 255)
        c2 = random.randint(0, 255)
        c3 = random.randint(0, 255)

        return (c1, c2, c3)

    @staticmethod
    def getRandomStr():
        '''获取一个随机字符串，每个字符的颜色也是随机的'''
        random_num = str(random.randint(0, 9))  # 数字
        random_low_alpha = chr(random.randint(97, 122))  # 小写字母
        # random_upper_alpha = chr(random.randint(65, 90)) # 大写字母
        # random_char = random.choice([random_num, random_low_alpha, random_upper_alpha])
        random_char = random.choice([random_num, random_low_alpha])
        return random_char

    def getValidCodeImg(self):
        # 获取一个Image对象，参数分别是RGB模式。宽150，高30，随机颜色
        # print(self.getRandomColor(),33)
        # (R128,G128,B128)
        # image = Image.new('RGB', (self.width, self.height), self.getRandomColor())
        image = Image.new('RGB', (self.width, self.height), (245, 245, 245))  # (245, 245, 245)白烟灰
        # 获取一个画笔对象，将图片对象传过去
        draw = ImageDraw.Draw(image)

        # 获取一个font字体对象参数是ttf的字体文件的目录，以及字体的大小
        font = ImageFont.truetype(web_conf.font_default_addr, size=self.font_size)

        temp = []
        for i in range(self.code_count):
            # 循环5次，获取5个随机字符串
            random_char = self.getRandomStr()

            # 在图片上一次写入得到的随机字符串,参数是：定位，字符串，颜色，字体
            draw.text((10 + i * 30, -2), random_char, self.getRandomColor(), font=font)

            # 保存随机字符，以供验证用户输入的验证码是否正确时使用
            temp.append(random_char)
        valid_str = "".join(temp)

        # 划线 # 噪点噪线
        for i in range(self.line_count):
            x1 = random.randint(0, self.width)
            x2 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            y2 = random.randint(0, self.height)
            draw.line((x1, y1, x2, y2), fill=self.getRandomColor())

        # 画点
        for i in range(self.point_count):
            draw.point([random.randint(0, self.width), random.randint(0, self.height)], fill=self.getRandomColor())
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            draw.arc((x, y, x + 4, y + 4), 0, 90, fill=self.getRandomColor())

        # 在内存生成图片
        from io import BytesIO
        f = BytesIO()
        image.save(f, self.img_format)
        data = f.getvalue()
        f.close()

        return data, valid_str


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
        if ip:
            self.ip = ip
        else:
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

    def cpu_count(self, logical=False):
        """
        cpu_count()	cpu_count(,[logical]):默认返回逻辑CPU的个数,当设置logical的参数为False时，返回物理CPU的个数。
        """
        return psutil.cpu_count(logical=logical)

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

    def cpu_core_num(self):
        """获取cpu的核数"""
        return multiprocessing.cpu_count()

    def get_glances_cpu_info(self):
        """
        从storage里获取cpu的全部信息
        {'total': 0.8, 'user': 0.5, 'nice': 0.0, 'system': 0.2, 'idle': 99.2, 'iowait': 0.0, 'irq': 0.0, 'softirq': 0.0, 'steal': 0.0, 'guest': 0.0, 'guest_nice': 0.0, 'time_since_update': 187668.0125412941, 'cpucore': 1, 'ctx_switches': 32830473, 'interrupts': 21091750, 'soft_interrupts': 21938257, 'syscalls': 0}
        total：所有 CPU 百分比的总和（空闲除外）（单位为百分比）
        system : 在内核空间中花费的时间百分比。系统 CPU 时间是在操作系统内核中运行代码所花费的时间（单位是百分比）
        user : CPU 在用户空间花费的时间百分比。用户 CPU 时间是在处理器上运行您的程序代码（或库中的代码）所花费的时间（单位为百分比）
        iowait : (Linux) : CPU 等待 I/O 操作完成所花费的时间百分比（单位为百分比）
        idle : 任何程序使用的 CPU 百分比。在计算机系统上运行的每个程序或任务都在 CPU 上占用一定的处理时间。如果 CPU 已完成所有任务，则它处于空闲状态（单位为百分比）
        irq：（Linux 和 BSD）：服务/处理硬件/软件中断所花费的时间百分比。时间服务中断（硬件+软件）（单位为百分比）
        nice : (Unix) : nice 值为正的用户级进程占用的时间百分比。在CPU已经使用了运行已被用户的进程的时间niced（单位为百分比）
        窃取: (Linux) : 当管理程序为另一个虚拟处理器提供服务时，虚拟 CPU 等待真实 CPU 的时间百分比（单位为百分比）
        ctx_switches：每秒上下文切换（自愿 + 非自愿）的次数。上下文切换是计算机的 CPU（中央处理单元）从一个任务（或进程）更改为另一个任务（或进程）同时确保任务不冲突的过程（单位为百分比）
        中断：每秒中断次数（单位为百分比）
        soft_interrupts：每秒软件中断数。在 Windows 和 SunOS 上始终设置为 0（单位为百分比）
        cpucore : CPU 核心总数（单位为number）
        time_since_update：自上次更新以来的秒数（单位为seconds）
        """
        api = RequestApi(ip=self.ip, url="/api/3/cpu", item=web_conf.default_monitoring_port)  # 调用61208的接口
        return api.get_public_api()

    def get_storage_cpu_info(self):
        api = RequestApi(ip=self.ip, url="/api/cpu/cpu_info", item=web_conf.default_storage_port)  # 调用8086的接口
        return api.get_public_api()

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

    def disk_io_counters(self, perdisk=True):
        """
        disk_io_counters([perdisk])：以命名元组的形式返回磁盘io统计信息(汇总的)，包括读、写的次数，读、写的字节数等。
        当perdisk的值为True，则分别列出单个磁盘的统计信息(字典：key为磁盘名称，value为统计的namedtuple)。
        """
        return psutil.disk_io_counters(perdisk=perdisk)

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
            这个类是包含系统所有的网络信息资源，继承了基础的SystemResources类
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

    def get_glances_network_info(self):
        """
            从glances里获取cpu的全部信息
        """
        api = RequestApi(ip=self.ip, url="/api/3/network", item=web_conf.default_monitoring_port)
        return api.get_public_api()

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
        # print(self.get_rate(self.get_key), 333333333)
        for key in key_info:
            if nc_name:
                if nc_name == key:
                    rate = {}
                    rate["nt_card"] = key
                    rate["input"] = net_in.get(key)
                    rate["Output"] = net_out.get(key)
                    rate['unit'] = 'KB/S'
                    all_network_rate.append(rate)
            else:
                rate = {}
                rate["nt_card"] = key
                rate["input"] = net_in.get(key)
                rate["Output"] = net_out.get(key)
                rate['unit'] = 'KB/S'
                all_network_rate.append(rate)
        return all_network_rate

    def get_a_network_rate(self, nc_name):
        """
            获取单个网卡速率
            ncname = 网卡名称
        """
        pass

    def get_key(self):
        """
            获取网卡名称。并且将网卡即时的流量字节记录
        """
        recv = {}
        sent = {}
        key_info = self.net_io_counters()  # 获取网卡名称
        for key in key_info:
            recv.setdefault(key, self.net_io_counters().get(key).bytes_recv)  # 各网卡接收的字节数
            sent.setdefault(key, self.net_io_counters().get(key).bytes_sent)  # 各网卡发送的字节数
        return key_info, recv, sent

    def get_rate(self, func):
        """
            计算一秒内数据的变化，继续速度计算
        """

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

    def get_node_info_network(self):
        """
            流量接收速率，流量发送速率，接收total ，发送的total
        """
        network_info = []
        glances_network_info = self.get_glances_network_info()  # 获取glances的网络信息
        for k, v in self.net_io_counters(pernic=True).items():
            network_info_dict = {}
            network_info_dict["network_name"] = k  # k 网卡名称
            for i in glances_network_info:
                if i["interface_name"] == k:  # 当两个网卡的信息查询一致时，我们把查询到的累计发送，累计接收取出来
                    network_info_dict["cumulative_rx"] = i["cumulative_rx"]
                    network_info_dict["cumulative_tx"] = i["cumulative_tx"]
                    network_info_dict["sent"] = i["tx"]
                    network_info_dict["recv"] = i["rx"]
                    network_info_dict['unit'] = 'bps'
                    network_info_dict['cumulative_unit'] = 'bytes'
                    # network_info_dict["sent"] = v.bytes_sent
                    # network_info_dict["recv"] = v.bytes_recv

            network_info.append(network_info_dict)
        return network_info

    def get_playback_network(self):
        """
({'bond1': snetio(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0, errin=0, errout=0, dropin=0, dropout=0),
'ens37': snetio(bytes_sent=10940, bytes_recv=259439731, packets_sent=120, packets_recv=3640925, errin=0, errout=0,
dropin=847, dropout=0),
'lo': snetio(bytes_sent=452562913, bytes_recv=452562913, packets_sent=2031636, packets_recv=2031636, errin=0, errout=0,
dropin=0, dropout=0),
'ens33': snetio(bytes_sent=278045095, bytes_recv=506609625, packets_sent=1249169, packets_recv=4975284, errin=0, errout=0,
dropin=847, dropout=0),
'ens38': snetio(bytes_sent=458516, bytes_recv=259597263, packets_sent=1644, packets_recv=3642273, errin=0, errout=0, dropin=0,
 dropout=0)},

 {'bond1': 0.0, 'ens37': 0.3515625, 'lo': 1.0986328125, 'ens33': 0.673828125, 'ens38': 0.3515625},
{'bond1': 0.0, 'ens37': 0.0, 'lo': 1.0986328125, 'ens33': 1.546875, 'ens38': 0.0})
     }

        """
        # print(self.get_rate(self.get_key), 3333)
        key_info, net_in, net_out = self.get_rate(self.get_key)
        # { bond1_input:1,bond1_output:2}
        playback_network = {}
        for key in key_info:
            for k, v in net_in.items():
                if key == k:
                    playback_network[k + "_input"] = v
                    # pass
            for k, v in net_in.items():
                if key == k:
                    playback_network[k + "_output"] = v
        return playback_network

    def create_network_playback(self, res, all_time):
        """
            # 由于结构有三层，较复杂
            用到一些矩阵思维
        """
        geometry = []  # 创建一个数据

        network_name_list = []
        nt_flag = False
        for i, ts in zip(res, all_time):
            i = eval(i)  # json 需要双引号，这个位置有隐患，由于数据是定时器写入，待改进
            if not nt_flag:
                for nt in i["network"]:  # 先用标志位获取网卡名称
                    network_name_list.append(nt)
            nt_flag = True
            nal_list = []
            for nal in network_name_list:
                if i["network"]:
                    nal_list.append(i["network"][nal])
                else:
                    nal_list.append(None)
            geometry.append(nal_list)

        geometry_dict = {}  # 得到一个结构key等于bond1_input values等于[[datetime.datetime(2021, 11, 17, 17, 1, 49, 873175), 0.0]的数据
        num = 0
        for nal in network_name_list:
            geo = []
            for g, t in zip(geometry, all_time):
                f = []  # 这个列表用来存放nt_card名字和data数据
                f.append(t)
                f.append(g[num])
                geo.append(f)
            num += 1
            geometry_dict[nal] = geo

        new_geometry_all = []
        for k, v in geometry_dict.items():
            new_geomtary_dict = {}  # 加工界面所需数据
            new_geomtary_dict["nt_card"] = k
            new_geomtary_dict["unit"] = "KB/S"
            new_geomtary_dict["data"] = v
            new_geometry_all.append(new_geomtary_dict)  #
        return new_geometry_all


class CPU(SystemCPU):
    def __init__(self, *args, **kwargs):
        """
            这个类是用来操作实际的CPU相关操作，继承了基础的SystemCPU类
            我希望关于CPU的拼接操作都在这个类的函数里完成
            这样url界面会更加整洁
        """
        super().__init__(*args, **kwargs)

    def __del__(self):
        return True

    def get_usage_rate(self):
        """
            获取CPU的使用率
        """
        return self.cpu_percent(interval=1)

    def get_node_info_cpu_info(self):
        """
            CPU核数，cpu个数，cpu处理器，cpu占用率
        """
        cpu_info_dict = {}
        cpu_info_dict["cpu_cores"] = self.cpu_core_num()  # CPU核数
        cpu_info_dict["cpu_count"] = self.cpu_count()  # cpu个数
        storage_cpu_info = self.get_storage_cpu_info()
        # print(storage_cpu_info, 4555555555555555555)
        if storage_cpu_info:  # cpu处理器
            if storage_cpu_info["code"] == 1:
                cpu_info_dict["processor"] = storage_cpu_info["message"]["Modelname"]  # cpu处理器
        else:
            cpu_info_dict["processor"] = ""
        cpu_info_dict["cpu_usage_rate"] = self.get_usage_rate()  # cpu占用率
        return cpu_info_dict

    def get_playback_cpu(self):
        """

        """
        return self.get_usage_rate()

    def create_cpu_playback(self, res, all_time):
        """

        """
        cpu_data = []
        for i, t in zip(res, all_time):
            i = eval(i)  # json 需要双引号，这个位置有隐患，由于数据是定时器写入，待改进
            cpu_usage_list = []
            cpu_usage_list.append(t)
            cpu_usage_list.append(i['cpu_usage'])
            cpu_data.append(cpu_usage_list)
        return cpu_data


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
        return memory_info.percent

    def get_node_info_memory_info(self):
        """
            内存大小，内存使用量，空闲量，内存占用率
            svmem(total=1199927296, available=612790272, percent=48.9, used=430395392, free=586121216, active=344543232, inactive=88977408, buffers=0, cached=183410688, shared=9347072, slab=75509760)
        """
        memory_dict = {}
        memory_info = self.virtual_memory()
        # print(memory_info, 444444444444444444444444444)
        memory_dict['total'] = memory_info.total  # 内存大小
        memory_dict['used'] = memory_info.used  # 使用量
        memory_dict['available'] = memory_info.available  # 可用的
        memory_dict['percent'] = memory_info.percent  # 内存占用率
        memory_dict['unit'] = 'KB'
        return memory_dict

    def get_playback_memory(self):
        """

        """
        memory_info = self.virtual_memory()
        return memory_info.percent

    def create_memory_playback(self, res, all_time):
        memory_data = []
        for i, t in zip(res, all_time):
            i = eval(i) # json 需要双引号，这个位置有隐患，由于数据是定时器写入，待改进
            memory_usage_list = []
            memory_usage_list.append(t)
            memory_usage_list.append(i['memory_usage'])
            memory_data.append(memory_usage_list)
        return memory_data


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

    def get_playback_io(self):
        """
        dict_items([('sda', sdiskio(read_count=30572, write_count=91873,
        read_bytes=1205129728, write_bytes=2159262720, read_time=102156,
        write_time=57466, read_merged_count=157, write_merged_count=17239,
         busy_time=107151)), ('sda1', sdiskio(read_count=1860, write_count=19,
          read_bytes=6390272, write_bytes=2189312, read_time=364, write_time=159,
          read_merged_count=0, write_merged_count=0, busy_time=375)),

        ('sda2', sdiskio(read_count=28682, write_count=91854, read_bytes=1197158400, write_bytes=2157073408, read_time=101780, write_time=57307, read_merged_count=157, write_merged_count=17239, busy_time=106806)), ('sr0', sdiskio(read_count=0, write_count=0, read_bytes=0, write_bytes=0, read_time=0, write_time=0, read_merged_count=0, write_merged_count=0, busy_time=0)), ('dm-0', sdiskio(read_count=28554, write_count=100573, read_bytes=1192259584, write_bytes=2122175488, read_time=102202, write_time=62238, read_merged_count=0, write_merged_count=0, busy_time=105001)), ('dm-1', sdiskio(read_count=201, write_count=8520, read_bytes=2719744, write_bytes=34897920, read_time=169, write_time=99259, read_merged_count=0, write_merged_count=0, busy_time=1854))])
        """
        disk_info_dict = {}
        for k, v in self.disk_io_counters().items():
            disk_info_dict[k + "_read"] = v.read_merged_count
            disk_info_dict[k + "_write"] = v.write_merged_count
        return disk_info_dict

    def create_io_playback(self, res, all_time):
        """
            # 由于结构有三层，较复杂
            用到一些矩阵思维
        """
        geometry = []  # 创建一个数据
        iops_name_list = []
        disk_flag = False
        for i, ts in zip(res, all_time):
            i = eval(i)  # json 需要双引号，这个位置有隐患，由于数据是定时器写入，待改进
            if not disk_flag:
                for nt in i["IOPS"]:  # 先用标志位获取网卡名称
                    iops_name_list.append(nt)
            disk_flag = True
            disk_list = []
            for nal in iops_name_list:
                if i["IOPS"]:
                    disk_list.append(i["IOPS"][nal])
                else:
                    disk_list.append(None)
            geometry.append(disk_list)

        geometry_dict = {}  # 得到一个结构key等于bond1_input values等于[[datetime.datetime(2021, 11, 17, 17, 1, 49, 873175), 0.0]的数据
        num = 0
        for dkn in iops_name_list:

            geo = []
            # print(len(all_time),4444444444444444,len(geometry),67677)
            for g, t in zip(geometry, all_time):
                f = []  # 这个列表用来存放nt_card名字和data数据
                f.append(t)
                f.append(g[num])

                geo.append(f)
            num += 1
            geometry_dict[dkn] = geo
        print(len(geometry_dict),444444444444)
        new_geometry_all = []
        for k, v in geometry_dict.items():
            new_geomtary_dict = {}  # 加工界面所需数据
            new_geomtary_dict["disk_name"] = k
            new_geomtary_dict["unit"] = "次"
            new_geomtary_dict["data"] = v
            new_geometry_all.append(new_geomtary_dict)  #

        return new_geometry_all


if __name__ == '__main__':
    print(SystemCPU([1, 23, 5, 687]))
