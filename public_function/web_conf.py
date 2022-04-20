# Create your tests here.
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
@file: 这里包含网站所有配置信息的集合文件
@time:2021/10/11
"""
import configparser

sys_default_password = "888888"

font_default_addr = "/opt/web/code/WebGUI/static/font/苹方黑体-中粗-繁.ttf"

conf_file_path = "/opt/configuration.ini"

verification_code_path = "/opt/web/code/WebGUI/templates/verification_code/"

server_all_name = {"nfs": "/api/nfs/service",
                   "smb": "/api/smb/service",
                   "ftp": "/api/ftp/service",
                   "iscsi": "/api/iscsi/service",
                   "sync": "/api/sync/service",
                   "firewall": "/api/firewall/service"}

download_log_path = "/opt/web/code/WebGUI/auction_log.xls"

default_storage_port = "storage_api_port"

default_monitoring_port = "monitoring_port"

role_joint = "ROLE_"

sys_code = {
    # success
    "210011": "数据添加成功",
    "210012": "数据删除成功",
    "210013": "数据修改成功",
    "210014": "获取数据成功",
    "210015": "数据保存成功",
    "210016": "数据查询成功",
    "210017": "文件上传成功",
    "210018": "服务设置成功",
    "210019": "操作设置成功",
    # error
    "110011": "数据重复添加",
    "110012": "数据添加失败",
    "110013": "数据删除失败",
    "110113": "数据删除失败,没有找到该条数据",
    "110014": "数据修改失败",
    "110015": "数据查询失败",

    "410011": "请求方式错误",
    "410012": "文件上传数量大于9个",
    "410013": "删除文件错误",
    "410014": "删除失败，请先删除标的物对应的费用信息",
    "410016": "删除失败，请先删除费用对应的标的物信息",

    "410017": "原始密码错误，无法修改",
    "410018": "该用户未分配团队",
    "410019": "验证码有误",
    "410020": "设置服务失败",

    "510011": "服务内部错误",
    "510012": "参数不完整",

    "610011": "数据完整性错误",

    "710011": "查询关系不存在",
    "710012": "执行出错",
    "710013": "您的账号暂时无权限操作",

    "800000": "登录成功",
    "800001": "用户名密码错误或者用户不存在",
    "800002": "用户名密码格式输入错误",
    "800003": "用户名密码错误",
    "800004": "用户名已存在",
    "800404": "用户查询失败，或者用户不存在",
    "800005": "团队名称已存在",
    "800006": "用户没有创建用户的权限",
    "800007": "用户权限异常",
    "800008": "团队中还有人员未移除该团队，请移除后再试",
    "800009": "该用户还有未处理的案件，请处理",
    "800010": "退出成功",
    "800011": "密码核验错误，请重新输入",
    "800012": "新用户密码两次核验错误，请重新输入",
    "800013": "删除失败，当前菜单中还有子菜单，请删除子菜单后重试",
    "800014": "角色唯一编码已存在,请修改后重试",
    "800015": "无法查询到该角色，角色id查询失败",
    "800016": "角色中还存在分配用户，请将用户移除后重试",
    "800017": "密码错误验证失败",
    "800018": "用户已经被禁用，请联系管理人员解锁",

    "900001": "无效的token",
    "900002": "登录状态过期请重新登录",
    "900200": "有效的token",
}
log_info_type = {
    "1001": "简单系统日志",
}
access_code = {
    "系统管理": "sys:manage",
    "用户管理": "sys:user:list",
    "角色管理": "sys:role:list",
    "菜单管理": "sys:menu:list",
    "磁盘管理": "stg:manage",
    "Disk管理": "stg:disk:list",
    "添加角色": "sys:role:add",
    "添加用户": "sys:user:add",
    "修改用户": "sys:user:update",
    "删除用户": "sys:user:del",
    "分配角色": "sys:user:role",
    "重置密码": "sys:user:repass",
    "修改角色": "sys:role:update",
    "删除角色": "sys:role:del",
    "分配权限": "sys:role:perm",
    "添加菜单": "sys:menu:add",
    "修改菜单": "sys:menu:update",
    "NAS管理": "nas:manage",
    "配额管理": "stg:quota:list",
    "Raid管理": "stg:raid:list",
    "用户/组管理": "stg:userGroup:list",
    "FTP": "stg:ftp:list",
    "SAN管理": "san:manage",
    "SAN": "stg:san:list",
    "存储系统日志": "log:sysLog:list",
    "业务日志": "log:servLog:list",
    "后台报警日志": "log:servLog:list",
    "业务日志设置": "log:setLog:check",
    "日志管理": "log:manage",
    "NFS": "stg:nfs:list",
    "CIFS": "stg:cifs:list",
    "节点状态": "sys:nodeStatus:check",
    "运行监控": "sys:nodeRun:check",
    "运行回放": "sys:playback:check",
    "服务状态": "sys:servStatus:check",
    "系统设置": "sys:setSys:check",
    "网络设置": "sys:setSys:check",
    "创建Target(SAN)": "stg:san:add",
    "开启/关闭服务(SAN)": "stg:san:on&off",
    "创建(FTP)": "stg:ftp:add",
    "删除(FTP)": "stg:ftp:del",
    "开启/关闭服务(FTP)": "stg:ftp:on&off",
    "权限设置(FTP)": "stg:ftp:authority",
    "创建(CIFS)": "stg:cifs:add",
    "开启/关闭服务(CIFS)": "stg:cifs:on&off",
    "编辑(CIFS)": "stg:cifs:update",
    "删除(CIFS)": "stg:cifs:del",
    "权限设置(CIFS)": "stg:cifs:authority",
    "创建(NFS)": "stg:nfs:add",
    "开启/关闭服务(NFS)": "stg:nfs:on&off",
    "删除(NFS)": "stg:nfs:del",
    "权限设置(NFS)": "stg:nfs:authority",
    "编辑(NFS)": "stg:nfs:update",
    "用户配额设置": "stg:quotaUser:update",
    "组配额设置": "stg:quotaGroup:update",
    "开启/关闭组配额": "stg:quota:on&off",
    "用户新建": "stg:user:add",
    "用户删除": "stg:user:del",
    "用户编辑": "stg:user:update",
    "密码重置": "stg:user:repass",
    "创建Raid": "stg:raid:add",
    "扩容Raid": "stg:raid:expand",
    "删除Raid": "stg:raid:del",
    "添加热备盘": "stg:raid:addHot",
    "删除热备盘": "stg:raid:delHot",
    "磁盘检测": "stg:disk:test",
    "磁盘创建分区表": "stg:disk:creatPartForm",
    "磁盘分区": "stg:disk:part",
    "磁盘格式化": "stg:disk:format",
    "磁盘逻辑卷设置": "stg:disk:lvSet",
    "磁盘卸载": "stg:disk:uninstall",
    "磁盘挂载": "stg:disk:mount",
    # "删除系统日志": "log:sysLog:del",
    "下载系统日志": "log:sysLog:down",
    "下载业务日志": "log:servLog:down",
    "下载报警日志": "log:alarmLog:down",
    "删除策略设置": "log:setLog:del",
    "备份策略设置": "log:setLog:backup",
    "自启设置(FTP)": "sys:servStatus:ftp",
    "自启设置(同步服务)": "sys:servStatus:sync",
    "自启设置(Windows共享)": "sys:servStatus:winShare",
    "自启设置(SNMP)": "sys:servStatus:snmp",
    "自启设置(防火墙)": "sys:servStatus:firewall",
    "自启设置(IPSAN)": "sys:servStatus:ipsan",
    "自启服务(Unix共享)": "sys:servStatus:unixShare",
    "系统时间设置": "sys:setSys:time",
    "系统开机": "sys:setSys:powerOn",
    "系统关机": "sys:setSys:powerOff",
    "系统重启": "sys:setSys:restart",
    "网卡绑定": "sys:net:bond",
    "网卡添加": "sys:net:add",
    "编辑网络接口": "sys:net:bondUpdate",
    "网卡解绑": "sys:net:bondDel",
    "网卡配置": "sys:net:update",
    "网卡删除": "sys:net:del",
    "编辑(SAN)": "stg:san:update",
    "删除(SAN)": "stg:san:del",
    "CHAP认证": "stg:san:chap",
    "创建组": "stg:group:add",
    "删除组": "stg:group:del",
    "编辑组": "stg:group:update",
    "权限管理": "perms:manage",
    "LDAP用户/组管理": "stg:LDAPuserGroup:list",
    "新建LDAP用户": "stg:LDAPuser:add",
    "删除LDAP用户": "stg:LDAPuser:del",
    "编辑LDAP用户": "stg:LDAPuser:update",
    "修改LDAP密码": "stg:LDAPuser:repass",
    "新建LDAP组": "stg:LDAPgroup:add",
    "删除LDAP组": "stg:LDAPgroup:del",
    "编辑LDAP组": "stg:LDAPgroup:update"
}

#  redis 配置
redis_port = "6379"
redis_password = "123456"
redis_db = "10"  # 这个是存储监控的专用库


class Configuration:
    """
        获取所有的配置文件
        某配置文件如下
        实例：
            [db]
                db_host = 127.0.0.1
                db_port = 69
                db_user = root
                db_pass = root
                host_port = 69
            [concurrent]
                thread = 10
                processor = 20
    """

    def __init__(self):
        """初始化配置文件，读取相对于的配置文件信息"""
        config = configparser.ConfigParser()
        config.read(conf_file_path, encoding="utf-8")
        self.config = config

    def get_sections(self):
        """
            获取配置文件的全部title
            print(self.config.sections())
            # >>>  ['db', 'concurrent']
        """
        return self.config.sections()

    def get_options(self, options_name):
        """
            获取某个配置文件title里的内容
            print(config.options("db"))
            # >>> ['db_host', 'db_port', 'db_user', 'db_pass', 'host_port']
        """
        return self.config.options(options_name)

    def get_items(self, items_name):
        """
            获取某个配置文件title里的内容
            print(config.options("db"))
            # >>>[('db_host', '127.0.0.1'),
             ('db_port', '69'), ('db_user', 'root'), ('db_pass', 'root'), ('host_port', '69')]
        """
        return self.config.items(items_name)

    def set_items(self, node, key, value):
        self.config.set(node, key, value)
        fh = open(conf_file_path, 'w')
        self.config.write(fh)  # 把要修改的节点的内容写到文件中
        fh.close()
        # self.config.write(open(conf_file_path, "w"))
        return True


if __name__ == '__main__':
    """
    [log]
        expiration_day = 30
        backups_day = 7 
        backups_time = "00:00:01" """
    print(Configuration().set_items("log", "expiration_day", "56"))
    print(Configuration().get_items("storage_api_port"))
