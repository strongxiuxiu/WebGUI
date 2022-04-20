from django.conf.urls import url

from system import views

urlpatterns = [
    url(r'^test$', views.test, name='login'),  # 测试
    url(r'^Test$', views.Test.as_view(), name='s'),  # 测试
    # 系统常规，登录退出验证码等
    # System general, login and exit verification code, etc
    url(r'^login$', views.Login.as_view(), name='login'),  # 登录验证
    url(r'^token/$', views.Login.as_view(), name='login'),  # 登录验证
    url(r'^logout$', views.user_logout, name='logout'),  # 退出登录
    url(r'^get_valid_img$', views.GetValidImg.as_view(), name='get_valid_img'),  # 登录页面验证码图片请求
    url(r'^userInfo$', views.get_user_info, name='get_user_info'),  # 获取用户的基本信息，用户名
    url(r'^user/compulsory/offline$', views.user_compulsory_offline, name='user_compulsory_offline'),  # 用户强制下线

    # 菜单相关配置操作
    url(r'^menu/nav$', views.get_menu_nav, name='GetMenuNav'),  # 获取用户的基本信息，用户名
    url(r'^menu/list$', views.menu_list, name='menu_list'),  # 系统菜单列表信息
    url(r'^menu/save$', views.menu_save, name='menu_save'),  # 菜单添加
    url(r'^menu/update$', views.menu_update, name='menu_update'),  # 菜单编辑
    url(r'^menu/delete/(\d+)$', views.menu_delete, name='menu_delete'),  # 菜单删除
    url(r'^menu/info/(\d+)$', views.menu_info, name='menu_info'),  # 菜单添加

    # 系统用户相关的操作，增删改查密码重置
    # System user related operations, add, delete, change, check password reset
    url(r'^user/save$', views.user_save, name='user_save'),  # 添加用户信息
    url(r'^user/update$', views.user_update, name='user_update'),  # 编辑用户信息
    url(r'^user/list$', views.user_list, name='user_list'),  # 获取用户列表
    url(r'^user/delete/(\d+)$', views.user_delete, name='role_delete'),  # 用户删除
    url(r'^user/repass$', views.user_reset_password, name='user_reset_password'),  # 用户密码重置
    url(r'^user/info/(\d+)$', views.user_info, name='user_info'),  # 用户信息获取
    url(r'^user/role/(\d+)$', views.user_role, name='user_role'),  # 用户角色信息配置
    url(r'^user/updatePass$', views.user_update_password, name='user_update_password'),  # 用户角色信息配置

    # 系统角色相关操作，增删改查等操作
    # Operations related to system roles, such as adding, deleting, modifying, and checking
    url(r'^role/save$', views.role_save, name='role_save'),  # 添加角色
    url(r'^role/update$', views.role_update, name='role_update'),  # 角色更新编辑
    url(r'^role/delete/(\d+)$', views.role_delete, name='role_delete'),  # 角色信息删除
    url(r'^role/list$', views.role_list, name='role_list'),  # 角色信息列表
    url(r'^role/info/(\d+)$', views.role_info, name='role_info'),  # 角色权限的信息
    url(r'^role/perm/(\d+)$', views.role_perm, name='role_perm'),  # 角色
    # CPU内存，网卡速率调用信息

    # /sys/role/perm/12
    url(r'^monitoring$', views.sys_monitoring, name='sys_monitoring'),  # 监控信息
    url(r'^monitor/playback$', views.monitor_playback, name='sys_monitoring'),  # 监控回放信息

    url(r'^node/info$', views.node_info, name='node_info'),  # 节点信息查询
    url(r'^all/serverstate$', views.all_service_state, name='all_service_state'),  # 所有的基础服务
    url(r'^all/server/set$', views.all_service_set, name='all_service_set'),  # 设置所有的服务状态

    url(r'^operation/log$', views.operate_log, name='operate_log'),  # 查询业务日志信息
    url(r'^alarm/log$', views.alarm_log, name='alarm_log'),  # 系统报警日志
    url(r'^storage/log$', views.storage_log, name='storage_log'),  # 系统存储日志

    url(r'^log/download$', views.download_log, name='download_log'),  # 查询业务日志下载
    url(r'^log/strategy$', views.log_strategy, name='log_strategy'),  # 修改业务日志策略配置
    url(r'^log/config/info$', views.log_configuration_information, name='log_configuration_information'),
    # 查询业务日志策略配置信息

    # 系统的网络设置
    url(r'^get/all/network_card_information$', views.all_network_card_information, name='network_card_information'),  # 获取网卡配置信息
    url(r'^add/network_card$', views.add_network_card_config, name='add_network_card_config'),  # 获取网卡配置信息
]

