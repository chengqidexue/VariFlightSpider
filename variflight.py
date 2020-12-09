import datetime
import time
import requests
import json
import xundaili

from lxml import etree

class VariFlightSpider(object):
    def __init__(self):
        self.start_url = 'http://www.variflight.com'
        self.file_name = datetime.datetime.now().strftime('%Y-%m-%d')+"-flight.json"    #写入的文件名 2020-12-08-flight.json，其中每天爬取的数据会存入以当天日期命名的json文件中

    '''
    获得所有的航班列表
    :return: list 访问的航班url列表
    '''
    def get_flight_list(self):
        headers = {}
        headers['User-Agent'] = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
        r = requests.get('http://www.variflight.com/sitemap.html?AE71649A58c77=', headers = headers)
        # print(r)
        selector = etree.HTML(r.text)

        #通过xpath获取需要的数据
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
        headers = xundaili.headers
        headers['Referer'] = 'http://www.variflight.com/sitemap.html?AE71649A58c77='            #必须在请求头中加入Referer字段，否则会返回406
        i = 0
        flag = False
        #尝试十次
        while(i < 10):
            try:
                print("第{}次尝试获取航班页面".format(i))
                r = requests.get(flight_url, headers=headers, proxies=xundaili.proxy, verify=False,allow_redirects=False, timeout = 5)
                r.encoding='utf8'
                flag = True
                break
            except:
                i = i + 1
        
        if flag:
            selector = etree.HTML(r.text)
            next_url_list = selector.xpath('//a[@class="searchlist_innerli"]/@href')
            if len(next_url_list) < 1 :
                return None
            else:
                return self.start_url+next_url_list[0]
        else:
            return None
        
    '''
    这个函数是为了获得那个需要的json的url
    @param next_url http://www.variflight.com/schedule/HRB-HGH-3U2014.html?AE71649A58c77=
    @param flight_url 作为访问的header里面的Referer是上一个跳转过来的url : http://www.variflight.com/flight/fnum/3U2014.html?AE71649A58c77=
    '''
    def get_json_url(self, next_url, flight_url):
        headers = xundaili.headers
        headers['Referer'] = flight_url
        #尝试十次
        i = 0
        flag = False
        #尝试十次
        while(i < 10):
            try:
                print("第{}次尝试获取json_url".format(i))
                r = requests.get(next_url, headers = headers, proxies=xundaili.proxy, verify=False,allow_redirects=False, timeout = 5)
                r.encoding='utf8'
                flag = True
                break
            except:
                i = i + 1
        if flag:
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
        else:
            return None
    
    '''
    把获得的时间标准化处理一下
    '''
    def timeformat(self,timestamp):
        timestr = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(timestamp)) if timestamp else '--'
        return timestr

    '''
    访问那个json_url
    提取出我们所需要的数据
    '''
    def parse_data(self, json_url):
        headers = xundaili.headers
        i = 0
        flag = False
        #尝试十次
        while(i < 10):
            try:
                print("第{}次尝试获取数据".format(i))
                r = requests.get(json_url, headers = headers, proxies=xundaili.proxy, verify=False,allow_redirects=False, timeout = 5)
                r.encoding='utf8'
                flag = True
                break
            except:
                i = i + 1
        if flag:
            myjson = r.json()
            data = myjson.get('data', {})
            scheduled_deptime = self.timeformat(data.get('scheduledDeptime',0)) # 计划出发
            actual_deptime = self.timeformat(data.get('actualDeptime',0)) # 实际出发
            scheduled_arrtime = self.timeformat(data.get('scheduledArrtime',0)) # 计划到达
            actual_arrtime = self.timeformat(data.get('actualArrtime',0)) # 实际到达
            data['scheduledDeptime'] = scheduled_deptime
            data['actualDeptime'] = actual_deptime
            data['scheduledArrtime'] = scheduled_arrtime
            data['actualArrtime'] = actual_arrtime
            #保存数据到文件中
            try:
                print(self.file_name)
                with open(self.file_name,'a',encoding="utf-8") as fp:
                    fp.write(json.dumps(data,ensure_ascii=False, indent=1)+",\n")
            except FileNotFoundError as err:
                pass
            except IOError as err:
                print('error'+ str(err))
            finally:
                fp.close()
            return data
        else:
            return None


def main():
    variflightspider = VariFlightSpider()
    '''
    获取一个航班列表的list
    '''
    flight_list = variflightspider.get_flight_list()
    # print(len(flight_list))
    i = 0

    flight_nums = 2000 #默认爬取数据大小，可以修改大小，最大为 len(flight_list)

    while i < flight_nums :
        print("======================================第{}次爬取数据===============================".format(i))
        i = i + 1
        try:
            flight_url = flight_list[12+i]
            next_url = variflightspider.get_next_url(flight_url)
            print(next_url)
            if next_url != None:
                json_url = variflightspider.get_json_url(next_url, flight_url)
                print(json_url)
                if json_url != None:
                    data = variflightspider.parse_data(json_url)
                    print(data)
        except:
            continue
    
if __name__ == "__main__":
    main()