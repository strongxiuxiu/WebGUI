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
@file: 这是一个将数据导为excel文件
@time:2021/10/11
"""

import os
import codecs

from openpyxl import Workbook

from public_function import web_conf

Alphabetic_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                   'U', 'V', 'W', 'X', 'Y', 'Z']


def excel_obj(monlist):
    wb = Workbook()
    sheet = wb.active
    sheet.title = "log_download"
    line1 = 1
    sheet["A%d" % line1].value = u'用户名'
    sheet["B%d" % (line1)].value = u'节点ip'
    sheet["C%d" % (line1)].value = u'事件内容'
    sheet["D%d" % (line1)].value = u'服务路径'
    sheet["E%d" % (line1)].value = u'操作时间'
    sheet["F%d" % (line1)].value = u'操作等级'
    sheet["G%d" % (line1)].value = u'备注'
    for i, vl in enumerate(monlist):
        line1 += 1
        sheet["A%d" % (line1)].value = vl['user_name']
        sheet["B%d" % (line1)].value = vl['login_ip']
        sheet["C%d" % (line1)].value = vl['action_info']
        sheet["D%d" % (line1)].value = vl['action_path']
        sheet["E%d" % (line1)].value = vl['action_time'].strftime('%Y-%m-%d %H:%M:%S')
        sheet["F%d" % (line1)].value = vl['operating_level']
        sheet["G%d" % (line1)].value = vl['remark']
    if not os.path.exists(web_conf.download_log_path):
        f = codecs.open(web_conf.download_log_path, "w", "utf-8")
        f.close()
    wb.save(web_conf.download_log_path)
