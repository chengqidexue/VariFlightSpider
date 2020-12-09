'''
由于目标网站有很强的反爬虫机制，访问过多和访问速度过快都会被封禁ip，这里采用了 讯代理 的动态转发机制。
这是绕过反爬机制的文件
其原理是：通过将爬虫请求转发给中间服务商，然后服务商随机选用ip访问网站，这个文件会生成一个header，我们访问的时候直接调用即可
'''
import sys
import time
import hashlib
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_version = sys.version_info

is_python3 = (_version[0] == 3)

orderno = "ZF20201275122ooRZz0"
secret = "a3d1500464fa4c08a7d971aa0a5777db"

ip = "forward.xdaili.cn"
port = "80"

ip_port = ip + ":" + port

timestamp = str(int(time.time()))              
string = ""
string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp

if is_python3:                          
    string = string.encode()

md5_string = hashlib.md5(string).hexdigest()                
sign = md5_string.upper()                             
#print(sign)
auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp

#print(auth)
proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
headers = {"Proxy-Authorization": auth, "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"}