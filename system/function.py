from public_function.tool import SystemNetwork


def back_children(res, sm_id, whole=None):
    # whole 代表了需要的数据结构不同
    # 回溯法之递归循环返回树结构
    children_list = []
    for i in res:
        children_dict = {}
        if sm_id == i["parent_id"]:
            if not whole:
                children_dict['orderNum'] = i['orderNum']
                children_dict['id'] = i['id']
                children_dict['name'] = i['perms']
                children_dict['title'] = i['name']
                children_dict['component'] = i['component']
                children_dict['icon'] = i['icon']
                children_dict['path'] = i['path']
                children_list.append(children_dict)
                children_dict["children"] = back_children(res, i['id'])
            else:
                children_dict['perms'] = i['perms']
                children_dict['orderNum'] = i['orderNum']
                children_dict['id'] = i['id']
                children_dict['name'] = i['name']
                children_dict['component'] = i['component']
                children_dict['icon'] = i['icon']
                children_dict['path'] = i['path']
                children_dict['type'] = i['type']
                children_dict['created'] = i['created']
                children_dict['updated'] = i['updated']
                children_dict['statu'] = i['statu']
                children_list.append(children_dict)
                children_dict["children"] = back_children(res, i['id'], whole=True)
    return children_list


# def back_children_list(self,res, sm_id):
#     # 回溯法之递归循环返回树结构


def get_key():
    print(SystemNetwork().net_io_counters)
    key_info = SystemNetwork().net_io_counters.keys()  # 获取网卡名称

    recv = {}
    sent = {}

    for key in key_info:
        recv.setdefault(key, SystemNetwork().net_io_counters(pernic=True).get(key).bytes_recv)  # 各网卡接收的字节数
        sent.setdefault(key, SystemNetwork().net_io_counters(pernic=True).get(key).bytes_sent)  # 各网卡发送的字节数

    return key_info, recv, sent
