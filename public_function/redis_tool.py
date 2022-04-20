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

# 导入redis模块
import redis


class RedisUtils:

    def __init__(self, host, port, password, db):
        '''
        初始化
        :param host:
        :param port:
        '''
        try:
            self.r = redis.StrictRedis(host=host, port=port, db=db, password=password, decode_responses=True)
        except Exception as e:
            print("redis连接失败,错误信息为%s" % e)

    def get_value(self, key):
        '''
        获取key的值
        :param key:
        :return:
        '''
        res = self.r.get(key)
        return res

    def get_ttl(self, key):
        '''
        获取key的过期时间
        :param key:
        :return:
        '''
        return self.r.ttl(key)

    def set_key_value(self, key, value, ex):
        '''
        往redis中设值
        :param key:
        :param value:
        :return:
        '''
        self.r.set(key, value, ex)

    def hset_key_values(self):
        self.r.hset(name="name", key="key1", value="value")


if __name__ == '__main__':
    pass
