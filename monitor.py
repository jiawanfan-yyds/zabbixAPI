from pyzabbix import ZabbixAPI, ZabbixAPIException
import json
import importlib.util
import argparse

def get_api(url, user, pw):
    api = ZabbixAPI(url)  # api地址
    api.login(user, pw)  # Zabbix用户名、密码
    return api


def get_template_group_id(api, name):
    group_re = api.hostgroup.get(output=['groupid'], filter={"name": [name]})
    if group_re:
        group_id = group_re[0]['groupid']
    else:
        group_id = ''
    return group_id

# def read_file(fn):
#     data = get_data(fn)
#     return data

def create_template(api, gid, name, alias):
    # 检查模板是否已存在
    existing_template = api.template.get(filter={'host': name}, output=['templateid'])

    if existing_template:
        # 如果模板已存在，返回现有模板的ID
        template_id = existing_template[0]['templateid']
        print("模板 '{}' 已经存在，其ID为：{}".format(name, template_id))
    else:
        # 如果模板不存在，创建模板
        ret = api.template.create(
            host=name,
            name=alias,
            groups={
                'groupid': gid
            }
        )
        template_id = ret['templateids'][0]
        print("模板 '{}' 创建成功，其ID为：{}".format(name, template_id))
    
    return template_id


# def get_template_id(api,tpl_name):
#     tpl_id = ''
#     try:
#         res = api.template.get(filter={'host':tpl_name}, output=['templateid'])
#         if res:
#             tpl_id = res[0]['templateid']

#     except ZabbixAPIException as e:
#             print(e)
#     return tpl_id


def create_item_trigger(api, template_id, template_name, tcp_status, ip_addr, status=0, delay='1m', expression='>=500', level=4):

    item_name = 'tcp_status_{0}'.format(tcp_status)   #监控项名称
    key = 'tcp.status[{0}]'.format(tcp_status)  #键值 
    item_id = api.item.create(
        name=item_name,
        key_=key,
        hostid=str(template_id),
        type=7,
        value_type=3,
        delay=delay
    )['itemids'][0]
    print("{} created success!".format(item_name))
    trigger_id = api.trigger.create(
        description="主机({0})的{1}状态异常".format(ip_addr,tcp_status),  #触发器名称
        expression='{%s:%s.last()}%s' % (template_name, key, expression),  #触发器表达式
        priority=level,
        status=status
    )['triggerids'][0]
    print("item_id:{}\n trigger_id:{}\n".format(item_id,trigger_id))


if __name__ == '__main__':

    # 创建命令行解析器
    parser = argparse.ArgumentParser(description="")

    # 添加命令行参数
    parser.add_argument("config_path", nargs="?", default="data.json", help="配置文件的路径，默认为 'data.json'")
    parser.add_argument("create_item_path", nargs="?", default= None, help="监控项文件的路径, 默认为None")

    # 解析命令行参数
    args = parser.parse_args()

    # 访问解析后的参数
    json_file_path = args.config_path
    create_item_path = args.create_item_path

   # 使用importlib导入监控项文件
    if create_item_path is not None:
        spec = importlib.util.spec_from_file_location("create_item", create_item_path)
        create_item = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(create_item)
        except FileNotFoundError:
            print(f"监控项文件不存在: {create_item_path}")
        except Exception as e:
            print(f"执行监控项文件时发生错误: {str(e)}")


    # 读取JSON文件中的数据
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)

    template_name=template_alias=data["template_name"]
    api=get_api(data["usr_api"]["url"], data["usr_api"]["usr"], data["usr_api"]["password"])  #创建api对象
    gid=get_template_group_id(api, data["gid_name"]) #获取模板分组id
    tpl_id=create_template(api, gid, template_name, template_alias) #创建模板
    # tpl_id=get_template_id(api,template_name)

    if create_item_path is not None:
        print("请创建自定义监控项")   
    else:
        try:
            create_item_trigger(api,tpl_id,template_name, "State", "192.168.5.206") #创建监控项、触发器 
        except Exception as e:
            print(e)
        

    

