from Crypto.Cipher import AES
import base64
import hashlib,requests
import time,json
from ..core import QPcollect
class Get_url(object):
    def __init__(self,start_time,**kwargs):
        self.url = kwargs["GET_URL"]   #请求的url
        self.key = kwargs["EAS_KEY"]     # 加密EAS时使用的key，只能是长度16,24和32的字符串
        self.md5_key = kwargs["MD5_KEY"]  # 加密md5时使用的key
        self.agent =  kwargs["AGENT"]     #第三方提供的编码
        self.start_time = start_time
    def handle(self):
        self.now_time = int(round(time.time() * 1000))
        data = "s=6&startTime=%s&endTime=%s" % \
               (str(int(self.start_time) - 5* 60 * 1000),self.start_time)
        encrypted_text = self.aes_encrypt(data)  #eas加密
        md5_str = self.md5_encrypt(str(self.agent) + str(self.now_time) + self.md5_key)  #md5加密
        url = "%s?agent=%s&timestamp=%s&param=%s&key=%s" % (
                                                            self.url,
                                                            self.agent,
                                                            self.now_time,
                                                            bytes.decode(encrypted_text),
                                                            md5_str)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','Connection': 'close'}
        while True:
            try:
                re_text = requests.get(url, headers=headers).text
            except Exception as e:
                time.sleep(5)
                continue
            if re_text:
                break
        return json.loads(re_text)

    def md5_encrypt(self,data):
        hl = hashlib.md5()
        hl.update(data.encode(encoding='utf-8'))
        return hl.hexdigest()

    def aes_encrypt(self,data):
        BS = AES.block_size
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        cipher = AES.new(self.key)
        encrypted = cipher.encrypt(pad(data))  # aes加密
        result = base64.b64encode(encrypted)  # base64 encode
        return result

GET_URL = {"KY":{
                "GET_URL":"https://kyrecord.ky206.com:190/getRecordHandle",
                "EAS_KEY":"DCE2A12F667F9BDC",
                "MD5_KEY":"B04569AF63BFAFA3",
                "AGENT": 70936,
            },
           "LC":{
                "GET_URL":"https://demorecord.lc8889.com:190/getRecordHandle",
                "EAS_KEY":"44E14CEFF548CADD",
                "MD5_KEY":"B12932528467099C",
                "AGENT":61117,
            },
           }
for site_name,data in GET_URL.items():
    while True:
        now_time = int(round(time.time() * 1000))
        print(site_name,str(now_time-16*60*60*1000))
        get_data = Get_url(str(now_time-16*60* 60 * 1000),**data)
        re_data = get_data.handle()
        print(re_data)
        if not re_data.get("s", None):
            time.sleep(5)
        elif int(re_data['d']['code']) not in (0, 16):
            time.sleep(5)
        else:
            collect_obj = QPcollect.Collect_handle()
            print(collect_obj.analyze_json(re_data['d']))
            break

