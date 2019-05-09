import threading
import requests

site_url_list = ["http://caiadmin.wxqq666.com","http://fxadmn.wxqq44.com/"]

def get_url(url):
    text = requests.get(url+"/ApiStat/auto").text
    print(text)

for url in site_url_list :
    t1 = threading.Thread(target=get_url,args=(url,))
    t1.setDaemon(True)
    t1.start()
