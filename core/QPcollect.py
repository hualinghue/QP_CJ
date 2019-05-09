import datetime,json,re,os
from conf import settings
from core import log_handle
from pymongo import MongoClient
from core import Get_url
import time
class Collect(object):
    def __init__(self,sys_args):
        self.last_time = 0
        self.sys_args = sys_args
        self.command_allowcator()


    def command_allowcator(self):
        if len(self.sys_args) == 3:
            Collect_proofread(self.sys_args)
        else:
            self.forever_run()
    def forever_run(self):
        # while True:
        #     if datetime.datetime.now().timestamp() - self.last_time > settings.cj_interval:
        #         print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"   开始采集")
        #         collect_obj = Collect_handle()
        #         collect_obj.handle()
        #         self.last_time = datetime.datetime.now().timestamp()
        collect_obj = Collect_handle()
        collect_obj.handle()

class Collect_handle(object):
    def __init__(self):
        self.logs = log_handle.Log_handle()
        self.link_mongo()
    def handle(self):
        # print("校队")
        # self._p()
        for name,data in settings.GET_URL.items():
            get_data = self.data_handle(data,name,)
            date_list = self.analyze_json(get_data["d"])
            if not date_list:
                print("无数据")
                continue
            self.write_mongo(date_list, name)
    def data_handle(self,data,name,):
        get_data = self.get_url(data,)
        print(name,get_data)
        if not get_data.get("s", None):
            time.sleep(5)
            return self.data_handle(data, name,)
        if int(get_data['d']['code']) not in (0, 16):
            time.sleep(5)
            return self.data_handle(data, name,)
        return get_data
    def save_local(self,date):
        # file_path = "../file/%s/" %(
        #     datetime.datetime.now().strftime("%Y%m%d"),
        # )
        # if not os.path.exists(file_path):
        #     os.makedirs(file_path)
        # with open(file_path+datetime.datetime.now().strftime("%H%M")+".txt",'w') as f:
        #     f.write(json.dumps(date))
        file_path = "../file/%s.txt" % (
            datetime.datetime.now().strftime("%Y%m%d"),
        )
        with open(file_path, 'w') as f:
            f.write(json.dumps(date))
    def get_url(self,data):
        get_data = Get_url.Get_url(interval=5,**data)
        return get_data.handle()
    def write_mongo(self,date_list,web_name):
        #写入mongo
        # Judge = False
        for date in date_list:
            print(date)
            game_id = date["GameID"]
            site_name = self.get_site_name(date['Accounts'])
            if not site_name:
                self.logs.write_err("ID:%s中%s解析错误"%(game_id,date["Accounts"]))
                continue
            table_name = "%s_%s_%s" %(web_name,"bets",site_name)
            table_obj = self.mongo_obj[table_name]
            # patents = {}    去重复
            # for itme in table_obj.find({"_id":{"$ne":0}}):
            #     if itme["GameID"] not in patents.keys():
            #         patents[itme["GameID"]] = itme
            #     else:
            #         table_obj.delete_one({"GameID":itme["GameID"]})
            # if table_obj.count() == 0:
            #     table_obj.ensure_index("GameID",unique=True)

            try:
                x = table_obj.insert_one(date)
                self.save_local(date)
                self.logs.write_acc("mongo:ID:%s写入成功" % game_id)
                print("mongo:ID:%s写入成功" % game_id)

            except Exception as e:
                print(e)
                print("mongo:ID:%s写入失败" % game_id)

            # if not table_obj.find_one({"GameID":game_id}):
            #     if not table_obj.insert(date):
            #         print("mongo:ID:%s写入失败" %game_id)
            #         self.logs.write_err("mongo:ID:%s写入失败" %game_id)
            #     else:
            #         self.logs.write_acc("mongo:ID:%s写入成功" % game_id)
            #         print("mongo:ID:%s写入成功" %game_id)
            #         Judge = True
            # else:
            #     print("mongo:ID:%s已写入" %game_id)
        # return Judge
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

class Collect_proofread(object):
    def __init__(self,sys_args):
        self.startTime = sys_args[1]
        self.num = sys_args[2]
        self.logs = log_handle.Log_handle()
        self.link_mongo()
        self.proofread()
    def handle(self):
        # print("校队")
        # self._p()

        for name,data in settings.GET_URL.items():
            get_data = self.data_handle(data,name)
            date_list = self.analyze_json(get_data["d"])
            if not date_list:
                print("无数据")
                continue
            self.write_mongo(date_list, name)
    def data_handle(self,data,name):
        print(name,data)
        if not data.get("s", None):
            time.sleep(5)
            return False
        if int(data['d']['code']) not in (0, 16):
            time.sleep(5)
            return False
        return data
    def save_local(self,date):
        file_path = "../file/proofread/"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(file_path+datetime.datetime.now().strftime("%H%M")+".txt",'w') as f:
            f.write(json.dumps(date))
    def get_url(self,data,starttime):
        get_data = Get_url.Get_url(interval=59,**data)
        return get_data.handle(starttime)
    def write_mongo(self,date_list,web_name):
        #写入mongo
        # Judge = False
        for date in date_list:
            print(date)
            game_id = date["GameID"]
            site_name = self.get_site_name(date['Accounts'])
            if not site_name:
                self.logs.write_err("ID:%s中%s解析错误"%(game_id,date["Accounts"]))
                continue
            table_name = "%s_%s_%s" %(web_name,"bets",site_name)
            table_obj = self.mongo_obj[table_name]
            if table_obj.count() == 0:
                table_obj.ensure_index("GameID",unique=True)

            try:
                self.logs.write_acc("mongo:ID:%s写入成功" % game_id)
                print("mongo:ID:%s写入成功" % game_id)
                table_obj.insert(date)
            except Exception as e:
                print("mongo:ID:%s写入失败" % game_id)
                self.logs.write_err("mongo:ID:%s写入失败" % game_id)

            # if not table_obj.find_one({"GameID":game_id}):
            #     if not table_obj.insert(date):
            #         print("mongo:ID:%s写入失败" %game_id)
            #         self.logs.write_err("mongo:ID:%s写入失败" %game_id)
            #     else:
            #         self.logs.write_acc("mongo:ID:%s写入成功" % game_id)
            #         print("mongo:ID:%s写入成功" %game_id)
            #         Judge = True
            # else:
            #     print("mongo:ID:%s已写入" %game_id)
        # return Judge
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
    def proofread(self):
            startTime = self.startTime
            for i in range(int(self.num)):
                for name, data in settings.GET_URL.items():
                    while True:
                        get_data = self.get_url(data,startTime)
                        if self.data_handle(get_data,name):
                            break
                        startTime = int(startTime) + 1000
                    date_list = self.analyze_json(get_data["d"])
                    if not date_list:
                        print("无数据")
                        continue
                    self.save_local(get_data)
                    self.write_mongo(date_list, name)
                    time.sleep(5)
                startTime =int(startTime) + 59 * 60 * 1000

