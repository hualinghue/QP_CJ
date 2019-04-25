from Crypto.Cipher import AES
import base64
import hashlib,requests
import time
class Get_url(object):
    def __init__(self,**kwargs):
        self.url = kwargs["url"]   #请求的url
        self.key = kwargs["key"]     # 加密EAS时使用的key，只能是长度16,24和32的字符串
        self.md5_key = kwargs["md5_key"]  # 加密md5时使用的key
        self.agent =  kwargs["agent"]     #第三方提供的编码
        self.now_time = int(round(time.time() * 1000))
        self.handle()
    def handle(self):
        data = "s=6&startTime=%s&endTime=%s" % \
               (str(self.now_time - 3 * 60 * 1000),str(self.now_time),)
        encrypted_text = self.aes_encrypt(data)  #eas加密
        md5_str = self.md5_encrypt(str(self.agent) + str(self.now_time) + self.md5_key)  #md5加密
        url = "%s?agent=%s&timestamp=%s&param=%s&key=%s" % (
                                                            self.url,
                                                            self.agent,
                                                            self.now_time,
                                                            bytes.decode(encrypted_text),
                                                            md5_str)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        return requests.get(url, headers=headers).text

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

