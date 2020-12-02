import requests;
import json;
import re;
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
    
    def get_flight_list(self):
        self.headers['User-Agent'] = self.user_agent.random
        r = requests.get('http://www.variflight.com/sitemap.html?AE71649A58c77=', headers = self.headers)
        # print(r)
        selector = etree.HTML(r.text)

        url_list = selector.xpath('//*[@class="list"]/a/@href')[1:]

        new_list = []
        for i in url_list:
            new_list.append(self.start_url + i)
        return new_list
    

def get_ip_list():
    user_agent = UserAgent()
    headers = {}
    headers['User-Agent'] = user_agent.random
    

        

def main():
    '''
    首先创建一个ip代理池
    '''
    pages = 1   # 定义爬取页数
    ua_num = 3  # 定义需生成user-agent个数
    target_url = 'https://www.baidu.com'    # 爬虫的目标地址，作为验证代理池ip的有效性
    proxy_list = kuaidaili.get_proxy(pages, ua_num, target_url)
    print(proxy_list)


    # variflightspider = VariFlightSpider()
    # flight_list = variflightspider.get_flight_list()
    # for flight in flight_list:
    #     print(flight)

if __name__ == "__main__":
    main()