from Crypto.Cipher import AES
import base64
import hashlib,requests
import time
startTime = int(round(time.time() * 1000))
key = "DCE2A12F667F9BDC"
get_url = "https://kyrecord.ky206.com:190/getRecordHandle"
agent = 70936
md5_key = "B04569AF63BFAFA3"

def aes_encrypt(data): 
    key="DCE2A12F667F9BDC"  #加密时使用的key，只能是长度16,24和32的字符串
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    cipher = AES.new(key)
    encrypted = cipher.encrypt(pad(data))  #aes加密
    result = base64.b64encode(encrypted)  #base64 encode
    return result

data = "s=6&startTime=%s&endTime=%s" %(str(startTime),str(startTime-3*60*1000))
encrypted_text = aes_encrypt(data)


#md5加密
md5_str = str(agent)+str(startTime)+md5_key
hl = hashlib.md5()
hl.update(md5_str.encode(encoding='utf-8'))

url = "%s?agent=%s&timestamp=%s&param=%s&key=%s" %(get_url,agent,startTime,bytes.decode(encrypted_text),hl.hexdigest())

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
print(requests.get(url,headers=headers).text)