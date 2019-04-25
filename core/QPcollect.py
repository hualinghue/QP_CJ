import datetime,json,re,os
from conf import settings
from core import log_handle
from pymongo import MongoClient
from core import Get_url
import time
class Collect(object):
    def __init__(self,sys_args):
        self.sys_args=sys_args
        self.last_time = 0
        self.command_allowcator()
    def command_allowcator(self):
        '''分检用户输入的不同指令'''
        if len(self.sys_args)<3:
            print("缺少参数")
            return
        elif self.sys_args[1] == "start":
            self.forever_run()
        else:
            print("参数1错误")
    def forever_run(self):
        while True:
            if datetime.datetime.now().timestamp() - self.last_time > settings.cj_interval:
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"   开始采集")
                collect_obj = Collect_handle()
                collect_obj.handle()
                self.last_time = datetime.datetime.now().timestamp()

class Collect_handle(object):
    def __init__(self):
        self.logs = log_handle.Log_handle()
        self.link_mongo()
    def handle(self,url_type=None):
        # print("校队")
        # self._p()
        for name,data in settings.GET_URL.items():
            get_data = self.data_handle(data,name)
            self.save_local(get_data)
            date_list = self.analyze_json(get_data["d"])
            if not date_list:
                print("无数据")
                return
            self.write_mongo(date_list, name)
            
    def data_handle(self,data,name):
        get_data = self.get_url(data)
        if not get_data.get("s", None):
            time.sleep(5)
            self.data_handle(data, name)
        if get_data['d']['code'] not in (0, 16):
            time.sleep(5)
            self.data_handle(data, name)
        return get_data

    def _p(self):
        path = "../file/20190424/"
        file_Iterator = os.walk(path)
        for item in file_Iterator:
            for file_name in item[2]:
                print("校队",file_name)
                with open("%s%s" % (path, file_name), 'r') as f:
                    for link in f.readlines():
                        date = json.loads(link)
                        date_list = self.analyze_json(date["data"])
                        self.write_mongo(date_list, "KY")
    def save_local(self,date):
        file_path = "../file/%s/" %(
            datetime.datetime.now().strftime("%Y%m%d"),
        )
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(file_path+datetime.datetime.now().strftime("%H%M")+".txt",'w') as f:
            f.write(json.dumps(date))
    def get_url(self,data):
        get_data = Get_url.Get_url(**data)
        return get_data.handle()
    def write_mongo(self,date_list,web_name):
        #写入mongo
        for date in date_list:
            print(date)
            game_id = date["GameID"]
            site_name = self.get_site_name(date['Accounts'])
            if not site_name:
                self.logs.write_err("ID:%d中%s解析错误")
                continue
            table_name = "%s_%s" %(web_name,site_name)
            table_obj = self.mongo_obj[table_name]
            if not table_obj.find_one({"GameID":game_id}):
                if not table_obj.insert(date):
                    print("mongo:ID:%s写入失败" %game_id)
                    self.logs.write_err("mongo:ID:%s写入失败" %game_id)
                else:
                    self.logs.write_acc("mongo:ID:%s写入成功" % game_id)
                    print("mongo:ID:%s写入成功" %game_id)
            else:
                print("mongo:ID:%s已写入" %game_id)
    def analyze_json(self,file_list):
        ##解析xml数据
        re_list = []
        if file_list.get("list",None):
            count = 0
            keys = file_list["list"].keys()
            for i in range(file_list["count"]):
                re_list.append(dict.fromkeys(keys))   ##生成空的字典
            for key,value in file_list["list"].items():
                for item in value:       ##循环每个字段的列表
                    try:
                        re_list[count][key] = float(item)
                    except ValueError:
                        re_list[count][key] = item
                    count+=1
                else:
                    count=0
        return re_list
    def get_site_name(self,site_name):
        req_name = re.search(r"_(\d\d\d)_", site_name)
        if req_name:
            return req_name.group(1)
        else:
            return None
    def link_mongo(self):
        """连接mongo"""
        user = settings.DB_USER
        pwd = settings.DB_PASSWORD
        server = settings.DB_HOST
        port = settings.DB_PORT
        db_name = settings.DB_NAME
        # url = 'mongodb://%s:%s@%s:%s/%s' % (user, pwd, server, port, db_name)
        mongo_client = MongoClient(host=server,port=port)
        db = mongo_client[db_name]
        try:
            db.authenticate(user,pwd)
            self.mongo_obj = db
            print("连接mongo成功")
        except Exception as e:
            print('连接mongo失败',e)
            self.logs.write_err("连接mongo失败")



collect_obj = Collect_handle()
collect_obj.handle()