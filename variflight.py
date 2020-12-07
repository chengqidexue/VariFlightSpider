from contextlib import nullcontext
from datetime import date
from numpy.core.fromnumeric import var
from numpy.lib.function_base import select
import requests;
import json;
import re;
from bs4 import BeautifulSoup as bs
import time;
import random;
from fake_useragent import UserAgent
import kuaidaili

from lxml import etree;

class VariFlightSpider(object):
    def __init__(self):
        self.start_url = 'http://www.variflight.com'
        self.user_agent = UserAgent()
        self.headers = {}
        self.ip_list = kuaidaili.read_ip()

    '''
    获得所有的航班列表
    '''
    def get_flight_list(self):
        self.headers['User-Agent'] = self.user_agent.random
        r = requests.get('http://www.variflight.com/sitemap.html?AE71649A58c77=', headers = self.headers)
        # print(r)
        selector = etree.HTML(r.text)

        url_list = selector.xpath('//*[@class="list"]/a/@href')[1:]

        flight_url_list = []
        for i in url_list:
            flight_url_list.append(self.start_url + i)
        return flight_url_list


    '''
    爬取航班页面，用xpath找到下一个需要跳转的页面
    //a[@class="searchlist_innerli"]/@href
    /schedule/HRB-HGH-3U2014.html?AE71649A58c77=
    @param flight_url :传入的航班url ： http://www.variflight.com/flight/fnum/3U2014.html?AE71649A58c77=
    '''
    def get_next_url(self,flight_url):
        headers = {}
        headers['User-Agent'] = self.user_agent.random
        headers['Referer'] = 'http://www.variflight.com/sitemap.html?AE71649A58c77='
        #获取一个ip
        #暂时先用本地ip测试一下
        r = requests.get(flight_url, headers = headers)
        selector = etree.HTML(r.text)

        next_url_list = selector.xpath('//a[@class="searchlist_innerli"]/@href')
        if len(next_url_list) < 1 :
            return None
        else:
            return self.start_url+next_url_list[0]


    '''
    这个函数是为了获得那个需要的json的url
    @param next_url http://www.variflight.com/schedule/HRB-HGH-3U2014.html?AE71649A58c77=
    @param flight_url 作为访问的header里面的Referer是上一个跳转过来的url : http://www.variflight.com/flight/fnum/3U2014.html?AE71649A58c77=
    '''
    def get_json_url(self, next_url, flight_url):
        headers = {}
        headers['User-Agent'] = self.user_agent.random
        headers['Referer'] = flight_url
        #获取一个ip
        #暂时先用本地ip测试一下
        r = requests.get(next_url, headers = headers)
        selector = etree.HTML(r.text)

        next_json_list = selector.xpath('//iframe/@src')
        if len(next_json_list) < 1 :
            return None
        else:
            #获得的url: https://flightadsb.variflight.com/flight-playback/3U2014/HRB/HGH/1607345700
            url = next_json_list[0]
            num = len('https://flightadsb.variflight.com/flight-playback/')
            #截取后半部分：3U2014/HRB/HGH/1607345700
            data_url = url[num:]
            values = data_url.split('/')
            fnum = values[0]
            forg = values[1]
            fdst = values[2]
            ftime = values[3]
            json_url = 'https://adsbapi.variflight.com/adsb/index/flight?lang=zh_CN&fnum={fnum}&time={time}&forg={forg}&fdst={fdst}'.format(fnum=fnum,time=ftime,forg=forg,fdst=fdst)
            return json_url
    
    '''
    访问那个json_url
    提取出我们所需要的数据
    '''
    def parse_data(self, json_url):
        headers = {}
        headers['User-Agent'] = self.user_agent.random

        r = requests.get(json_url, headers = headers)

        myjson = r.json()
        data = myjson.get('data', {})
        #保存数据到文件中
        try:
            with open("flight.json",'a',encoding="utf-8") as fp:
                fp.write(json.dumps(data,ensure_ascii=False)+",\n")
        except FileNotFoundError as err:
            pass
        except IOError as err:
            print('error'+ str(err))
        finally:
            fp.close()
        
        return data

        # fnum = data.get('fnum','--')                                               # 航班号
        # aircname = data.get('airCName','--')                                      # 航空公司
        # scheduleddeptime = self.timeformat(data.get('scheduledDeptime',0))         # 计划出发
        # actualdeptime = self.timeformat(data.get('actualDeptime',0))               # 实际出发
        # forgaptcname = data.get('forgAptCname','--')                               # 出发地
        # scheduledarrtime = self.timeformat(data.get('scheduledArrtime',0))         # 计划到达
        # actualarrtime = self.timeformat(data.get('actualArrtime',0))               # 实际到达
        # fdstaptcname = data.get('fdstAptCname','--')                               # 到达地
        # status = '取消' if actualArrtime == '--' else '到达'                        # 状态
        # value = ','.join([fnum,aircname,scheduleddeptime,actualdeptime,forgaptcname,scheduledarrtime,actualarrtime,fdstaptcname,status])




#     def parse_data(self,):
#         ip_list = self.get_ip()
#         while(1):
#             try:
#                 self.headers['User-Agent'] = self.ua.random
#                 ip = random.choice(ip_list)
#                 r = requests.get(url_data,headers=self.headers,proxies={'http':ip,'https':ip},timeout=1)
#                 json= r.json()
#                 data = json.get('data',{})
#                 break
#             except:
#                 ip_list = self.get_ip()
        
#         fnum = data.get('fnum','--') #航班号
#         airCName = data.get('airCName','--') # 航空公司
#         scheduledDeptime = self.timeformat(data.get('scheduledDeptime',0)) # 计划出发
#         actualDeptime = self.timeformat(data.get('actualDeptime',0)) # 实际出发
#         forgAptCname = data.get('forgAptCname','--') # 出发地
#         scheduledArrtime = self.timeformat(data.get('scheduledArrtime',0)) # 计划到达
#         actualArrtime = self.timeformat(data.get('actualArrtime',0)) # 实际到达
#         fdstAptCname = data.get('fdstAptCname','--') # 到达地
#         status = '取消' if actualArrtime == '--' else '到达' # 状态
#         value = ','.join([fnum,airCName,scheduledDeptime,actualDeptime,forgAptCname,scheduledArrtime,actualArrtime,fdstAptCname,status])
# #        print(value)
#         with open('f:\\data\\{0}.csv'.format(fdata),'a') as f:
#             f.write(value + '\n')





def main():
    '''
    首先创建一个ip代理池
    '''
    # pages = 1   # 定义爬取页数
    # ua_num = 3  # 定义需生成user-agent个数
    # target_url = 'https://www.baidu.com'    # 爬虫的目标地址，作为验证代理池ip的有效性
    # proxy_list = kuaidaili.get_proxy(pages, ua_num, target_url)
    # print(proxy_list)

    '''
    验证一个能否正确创建ip池
    '''
    # ip_list = variflightspider.ip_list
    # for ip in ip_list:
    #     print(ip)

    # url_fnums = variflightspider.get_fnums_from_txt()
    # print(url_fnums)


    variflightspider = VariFlightSpider()

    '''
    获取一个航班列表的list
    '''
    # flight_list = variflightspider.get_flight_list()
    # for flight in flight_list:
    #     print(flight)

    '''
    验证能否正确获得下一个url
    '''
    flight_url = 'http://www.variflight.com/flight/fnum/3U2014.html?AE71649A58c77='
    next_url = variflightspider.get_next_url(flight_url)
    print(next_url)
    json_url = variflightspider.get_json_url(next_url, flight_url)
    print(json_url)
    data = variflightspider.parse_data(json_url)
    print(data)
    
if __name__ == "__main__":
    main()