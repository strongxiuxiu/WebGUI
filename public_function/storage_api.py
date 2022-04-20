"""
The best sentence

1 Don’t hate your enemy, or you will make wrong judgment.
2 I'm gonna make him an offer he can't refuse.
3 A friend should always underestimate your virtues and an enemy overestimate your faults.
4 You know...the world’s full of lonely people afraid to make the first move
5 I suffer that slight alone,because I’m not accepted by my own people,
    because i’m not like them either! So if I'm not black enough and if I'm not white enough,
    then tell me, Tony, what am I !?
6 whatever you do,do it a hundred percent.when you work,when you laugh,laugh,when you eat,eat like it's your last meal.

@author:StrongXiuXiu
@file:
@time:2021/10/11
"""
import json
import requests
from requests.exceptions import RequestException

from public_function.web_conf import Configuration

"""
    这是存储apiURL的调用d
"""


class RequestApi(object):
    def __init__(self, ip, url, item="storage_port", time=None, params=None, headers=None):
        """
        :param ip: 用户访问ip
        :param url: 用户访问url
        :param item: 用户想访问的配置文件【xxx】 内容 /etc/configuration.ini 默认配置文件目录
        :param time: 请求返回超时时间
        :param params: 请求参数
        :param headers: 请求头
        """
        self.ip = ip
        self.port = Configuration().get_items(item)[0][1]
        self.url = url
        self.params = params
        self.headers = headers
        self.http_url = "http://"
        self.time = time

    def __str__(self):
        explain = "这是存储api接口的调用整合的类"
        return explain

    def joint_url(self):
        """
            拼接请求的url
            self.http_url = "http://" + str(self.ip) = "192.168.1.1" + str(self.port) =8899 +  self.url = /api/get
        """
        get_url = self.http_url + str(self.ip) + ":" + str(self.port) + self.url
        return get_url

    def get_public_api(self, ):
        """
            请求拼接好的url，带入参数返回数据
        """
        try:
            url = self.joint_url()
            if self.params:
                html = requests.get(url, params=self.params, timeout=self.time)
                print(html, 4555666)
            else:
                html = requests.get(url)
            if html.status_code == 200:
                if html.text:
                    return json.loads(html.text)
                else:
                    return html  # (fio测试返回为空,比较特殊)
        except RequestException:
            print('无法访问%s接口' % self.ip)
            return None


""""""


class GetIP(object):
    """获取ip"""

    def __str__(self):
        explain = "获取机器IP"
        return explain

    def __init__(self):
        pass

    @staticmethod
    def get_self_ip():
        # 获取本机IP
        """
        Configuration().get_items(item)[0][1]
        """
        # oneself_node = Configuration().get_items('a_ip')[0][1]
        # self_ip = oneself_node[0][1]
        return Configuration().get_items('oneself_ip')[0][1]

    @staticmethod
    def get_all_ip():
        # 获取机器所有的节点和IP
        system_ip = Configuration(inifile_bacitmes='node_ip').send_item_back_value()
        return system_ip

    @staticmethod
    def get_nodename_back_ip(node_name):
        # 发送节点名称，返回ip
        node_ip = Configuration().send_item_back_value()
        for i in node_ip:
            if i[0] == node_name:
                return i[1]
        return None

    @staticmethod
    def get_ip_back_nodename(ip):
        # 发送ip，返回节点名称
        node_ip = Configuration().send_item_back_value()
        for i in node_ip:
            if i[1] == ip:
                return i[0]
        return None
