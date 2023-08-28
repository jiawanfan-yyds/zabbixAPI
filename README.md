## 本项目利用zabbix提供的api实现自动化创建监控项
>注意：本项目测试的API为`zabbix5.0`，其他版本暂未测试

## 开始安装

>Linux
 1. 安装Python3环境

``` shell
sudo apt-get install python3.10
```

 2. 安装pyzabbix

``` shell
pip3 install -r requirements.txt
```

 3. 获取项目

``` shell
git clone https://github.com/jiawanfan-yyds/zabbixAPI.git
```

## 运行
``` shell
python3 monitor.py
```

## 其他参数
| 参数                | 解释                                           |
| ------------------- | ---------------------------------------------- |
| --config_path       | 配置文件的路径，默认为 `data.json`            |
| --create_item_path  | 监控项文件的路径，默认为 None                  |

## 支持自定义监控项
>支持python自定义监控项方法，可直接修改`monitor.py`中的方法，也可使用`--create_item_path`导入自定义监控项


