# -*- coding: utf-8 -*-
import requests
#import cx_Oracle
import json
import datetime
import pymysql
import re
import time

import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  
from selenium.webdriver.support import expected_conditions as EC
from dianping import get_dianping

class StopSpyder(BaseException):pass

class NewsGain(object):

    # 初始化
    def __init__(self):
        self.login = False
        self.data = pd.DataFrame(columns = ["source","spot","time","userid","content","star"])


    # 连接数据库
    def con_mysql(self):
        db = pymysql.connect('localhost','root','mysql0601','arvin', charset='utf8')
        return db

    # 查询数据库的最新日期
    def get_last_time(self,source,spot):
        db = self.con_mysql()
        # 创建cursor游标对象
        cursor = db.cursor()

        row_1 = '0'
        # 插入语句
        sql = 'select max(comment_time) time from t_jiangsu_tourism_sight where source_web =%s and sight_name =%s'
        try:
            row_count = cursor.execute(sql,(source,spot))
            row_1 = cursor.fetchone()[0]
#            print(row_count,row_1)
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)
        # 关闭数据库连接
        cursor.close()
        db.close()

        if row_1 is None:
            row_1 = '0'

        return row_1


    #插入数据库Oracle
    def inOrcl(self,data):
        # 将dataframe对象转化为list
        L = np.array(data).tolist()
        # 创建数据库连接
        db = cx_Oracle.connect('arvin', '11111', '127.0.0.1:1521/orcl')
        # 创建游标对象
        cursor = db.cursor()
        # 插入语句
        cursor.prepare('insert into test(source,spot,time,userid,content,star) values(:1,:2,:3,:4,:5,:6)')
        # 批量插入
        cursor.executemany(None,L)
        # 提交事务
        db.commit()

    #插入数据库Mysql
    def inMysql(self,data):
        # 将dataframe对象转化为list
        L = np.array(data).tolist()
        # 获取数据库连接
        db = self.con_mysql()
        # 创建cursor游标对象
        cursor = db.cursor()
        # 插入语句
        sql = 'insert into t_jiangsu_tourism_sight(source_web,sight_name,comment_time,comment_user,comment_text,comment_score) values(%s,%s,%s,%s,%s,%s)'
        try:
            cursor.executemany(sql,L)
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)
        # 关闭数据库连接
        cursor.close()
        db.close()

    # 获取BeautifulSoup对象
    def getBS(self,url,params = None):
        #定义访问文件头
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        # 访问网页
        req = requests.get(url, headers = headers, params=params)
        # 获取编码
        charset = req.encoding
        # 获取网页内容
        content = req.text
        # 先根据原编码转化为字节bytes，转化为utf-8字符串str
        content = content.encode(charset).decode('utf-8')
        # 获取bs对象，类型未lxmlfin
        soup = BeautifulSoup(content, 'lxml')

#        soup = BeautifulSoup(content, 'html.parser')
        # 去掉style标签
        [s.extract() for s in soup('style')]
        # 返回soup
        return soup

    # 保存数据到data
    def saveData(self, source, spot, time, userid, content, star):

        index = self.data.shape[0]
        self.data.at[index,'source'] = source
        self.data.at[index,'spot'] = spot
        self.data.at[index,'time'] = time
        self.data.at[index,'userid'] = userid
        self.data.at[index,'content'] = content
        self.data.at[index,'star'] = star

    # Test 导出csv文件
    def toCSV(self,data,charset = 'utf-8'):
        try:
            self.data.to_csv('test.csv', index = False, encoding = charset)
        except Exception as e:
            pass

    #新闻爬取入口
    def startGain(self,url):
        if url[12] == 'd':
           returnlist = get_dianping(url)
           for one in returnlist:
               if one[1] > self.get_last_time(u'点评',one[0][:3]):
                   self.saveData(u'点评', one[0][:3],one[1],one[2],one[3],one[4])
                   pass
        elif url[9] == 'm':
           self.meituan(url = url)
           pass
        elif url[7:9] == 'ti':
            self.lvmama(url = url)
            pass
        elif url[12:17] or url[14:19] == 'qunar':
           self.qunar(url = url)
           pass
        else:
            pass


######################################具体爬取网站####################################

    # 美团网        
    def meituan(self, url):
        # 美团评价采用动态网页，访问对应的接口解析JSON即可
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

        # 定义源
        source = u'美团'

        # 访问网页
        req = requests.get(url,headers = headers)

        # 获取内容
        charset = req.encoding
        content = req.text.encode(charset).decode('utf-8')

        # 转化为JSON对象
        json_con = json.loads(content)

        # 获取评论列表
        comment_list = json_con['data']['commentDTOList']

        # 根据url中的poiId判断地点
        if url[58:60] == '16':
            spot = '伊芦山'
        else:
            spot = '大伊山'

        # 获取具体内容
        for comment in comment_list:

            # 地点
#            spot = comment['menu'][:5]
            # 评论时间
            comment_time = datetime.datetime.strptime(comment['commentTime'],'%Y年%m月%d日')
            time = datetime.datetime.strftime(comment_time,"%Y-%m-%d %H:%M")
            # 用户
            userid = comment['userName']
            # 内容
            content = comment['comment']
            # 星级
            star = comment['star']/10

            if time > self.get_last_time(source,spot):
                self.saveData(source,spot,time,userid,content,star)

#        self.toCSV(data)
#        self.inMysql(data)


    # 大众点评是javascript渲染的页面，html返回的评论信息不全，考虑采用selenium
    def dazhong(self, url):
        self.loginDianPing()
        # 定义新闻源
        source = u'大众'
                # 访问网页
        self.driver.get(url)
#        self.dr.get('http://www.dianping.com/shop/5400289')
        time.sleep(3)
        # 获取景点名称
        try:
            wholeSpot = self.driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[1]/h1").text
        except:
            wholeSpot = self.driver.find_element_by_xpath("/html/body/div[2]/div/div[2]/div[1]/h1").text
        spot = wholeSpot[:3]
        wholeSpot = spot
#        wholeSpot = '潮河湾'
        print(wholeSpot)

        try:
            while True:
                # 获取当前页面的评论

                currentPageCommentItem = self.driver.find_elements_by_class_name("comment-item")

                # 遍历每一条评论
                for index,item in enumerate(currentPageCommentItem):
                    date = item.find_element_by_class_name("time").text         # 评论的时间
                    date = datetime.datetime.strptime(re.sub("\D","",date)[:8], "%Y%m%d")
                    if self.stopSpyder(source, wholeSpot, date):                                   # 判断是否需要继续爬取
                        raise StopSpyder
                    else:
                        # 爬取信息
                        userId = item.find_element_by_class_name("name").text
                        print(userId)
                        try:
                            item.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[8]/ul/li['+ str(index[0]) +']/div/div[1]/a').click()
                            content = item.find_element_by_class_name("desc J-desc").text
                        except:
                            content = item.find_element_by_class_name("desc").text
                        star = item.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[8]/ul/li[1]/div/p[1]/span").get_attribute("class")
                        star = round(int(re.sub("\D","",star)) / 10)

                        # 保存数据
                        index = self.data.shape[0]
                        self.data.at[index,"time"] = datetime.datetime.strftime(date,"%Y%m%d")
                        print('time:{}'.format(datetime.datetime.strftime(date,"%Y%m%d")))
                        self.data.at[index,"id"] = userId
                        print('id:{}'.format(userId))
                        self.data.at[index,"source"] = source
                        print('source:{}'.format(source))
                        self.data.at[index,"spot"] = spot
                        print('spot:{}'.format(spot))
                        self.data.at[index,"content"] = content
                        print('content:{}'.format(content))
                        self.data.at[index,"star"] = star
                        print('star:{}'.format(star))

                        self.data.to_csv("result.csv",index=False,encoding="utf-8")
                break


        except StopSpyder:
            pass
        except Exception as e:
            print(e)

#        # 访问网页
##        soup = self.getBS(url)
#        
##        news = soup.find_all(class_ = 'comment-item')
#          

    def loginDianPing(self):
        if not self.login:
            # 登陆网站
            self.driver.get('http://account.dianping.com/login')
            WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(self.driver.find_element_by_xpath('//iframe[contains(@src, "account")]')))
            self.driver.find_element_by_class_name('bottom-password-login').click()
            self.driver.find_element_by_id('tab-account').click()
            self.driver.find_element_by_id('account-textbox').clear()
            self.driver.find_element_by_id('account-textbox').send_keys('15366181451')
            self.driver.find_element_by_id('password-textbox').clear()
            self.driver.find_element_by_id('password-textbox').send_keys('hongxin12')
            self.driver.find_element_by_id('login-button-account').click()
            cur_url = self.driver.current_url
            while cur_url == self.driver.current_url:
                time.sleep(5)
            self.driver.switch_to_default_content()
            self.driver.get('http://www.dianping.com/shop')
            time.sleep(3)
            self.login = True

    # 驴妈妈
    def lvmama(self, url):

        # 获取参数信息
        lvDir = {'http://ticket.lvmama.com/scenic-103108':{'currentPage':9,'placeId':'103108','spot':'大伊山'},
                 'http://ticket.lvmama.com/scenic-11345447':{'currentPage':None,'placeId':'11345447','spot':'伊甸园'},
                 'http://ticket.lvmama.com/scenic-11345379':{'currentPage':None,'placeId':'11345379','spot':'伊芦山'}
                 }
        if lvDir[url]['currentPage'] is None:
            return 

        # 网站来源
        source = u'驴妈妈'
        spot = lvDir[url]['spot']
        # 驴妈妈POSTurl
        rurl = 'http://ticket.lvmama.com/vst_front/comment/newPaginationOfComments'


        # 获取参数
        for i in range(1,lvDir[url]['currentPage']):
            print(i)

            # 配置参数
            params = {
            'currentPage':i,
            'isBest':None,
            'isELong':'N',
            'isPicture':None,
            'isPOI':'Y',
            'placeId':lvDir[url]['placeId'],
            'placeIdType':'PLACE',
            'productId':None,
            'totalCount':72,
            'type':'all'
            }

            # 获取soup对象

            soup = self.getBS(rurl,params)
            # 获取评论列表
            comment_list = soup.find_all(class_ = 'comment-li')
            # 遍历新闻，获取每条的详细信息
            for comment in comment_list:

                star = comment.find(class_ = 'ufeed-level').i.get('data-level')
                userid = comment.find(class_ = 'com-userinfo').p.a.get('title')
                time = comment.find(class_ = 'com-userinfo').p.em.text
                content = comment.find(class_ = 'ufeed-content').text.replace('\r\n','').replace(' ','')
#                print(content)

                if time > self.get_last_time(source,spot):
                    self.saveData(source,spot,time,userid,content,star)



    # 去哪儿    
    def qunar(self, url):
        # 网站来源
        source = u'去哪儿'

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

        url[:45]
        qunar_dir = {'http://piao.qunar.com/ticket/detail_110216625':{'sightId':31828,'spot':u'大伊山'}, # 大伊山
                     'http://travel.qunar.com/p-oi10010340-yilushan':{'sightId':None,'spot':u'伊芦山'}, # 伊芦山
                     'http://travel.qunar.com/p-oi10025389-chaohewa':{'sightId':None,'spot':u'潮河湾'}, # 潮河湾
                     'http://piao.qunar.com/ticket/detail_526407124':{'sightId':467928,'spot':u'伊甸园'}  # 伊甸园
                     }

        sightId = qunar_dir[url[:45]]['sightId']
        spot = qunar_dir[url[:45]]['spot']

        if sightId is None:
            return

        url = 'http://piao.qunar.com/ticket/detailLight/sightCommentList.json?sightId=%s&index=1&page=1&pageSize=500&tagType=0'%(sightId)

#        print(url)

        # 访问网页
        req = requests.get(url,headers = headers)

        # 获取内容
        charset = req.encoding
        content = req.text.encode(charset).decode('utf-8')

        # 转化为JSON对象
        json_con = json.loads(content)

        # 获取页面数
#        pages = json_con['data']['tagList'][0]['tagNum']

        # 获取评论列表
        comment_list = json_con['data']['commentList']

        # 获取具体内容
        for comment in comment_list:
            userid = comment['author']
            com_time = comment['date']
            star = comment['score']
            content = comment['content']
#            print(content)

            if com_time > self.get_last_time(source,spot):
                self.saveData(source,spot,com_time,userid,content,star)

#        self.inMysql(self.data)


# 程序入口
if __name__ == "__main__":
    # 目标爬取网站
    sourcetUrl = ['http://i.meituan.com/xiuxianyule/api/getCommentList?poiId=1262239&offset=0&pageSize=1000&sortType=0&mode=0&starRange=10%2C20%2C30%2C40%2C50&tag=%E5%85%A8%E9%83%A8', #'http://www.meituan.com/xiuxianyule/1262239/' #大伊山
                 'http://i.meituan.com/xiuxianyule/api/getCommentList?poiId=165644028&offset=0&pageSize=1000&sortType=0&mode=0&starRange=10%2C20%2C30%2C40%2C50&tag=%E5%85%A8%E9%83%A8', #'http://www.meituan.com/xiuxianyule/165644028/' #伊芦山
                 'https://www.dianping.com/shop/5400289/review_all', #大伊山
                 'https://www.dianping.com/shop/11884431/review_all', #潮河湾
                 'https://www.dianping.com/shop/98669133/review_all', #伊芦山
                 'https://www.dianping.com/shop/14713390/review_all', #伊芦山
                 'https://www.dianping.com/shop/98241681/review_all', #伊芦山
                 'http://ticket.lvmama.com/scenic-103108', #驴妈妈大伊山
                 'http://ticket.lvmama.com/scenic-11345447', #驴妈妈伊甸园
                 'http://ticket.lvmama.com/scenic-11345379', #驴妈妈伊芦山梅园
                 'http://piao.qunar.com/ticket/detail_1102166256.html?st=a3clM0QlRTUlQTQlQTclRTQlQkMlOEElRTUlQjElQjElMjZpZCUzRDMxODI4JTI2dHlwZSUzRDAlMjZpZHglM0QxJTI2cXQlM0RuYW1lJTI2YXBrJTNEMiUyNnNjJTNEV1dXJTI2YWJ0cmFjZSUzRGJ3ZCU0MCVFNiU5QyVBQyVFNSU5QyVCMCUyNnVyJTNEJUU4JUJGJTlFJUU0JUJBJTkxJUU2JUI4JUFGJTI2bHIlM0QlRTYlOUMlQUElRTclOUYlQTUlMjZmdCUzRCU3QiU3RA%3D%3D#from=qunarindex', # 去哪儿大伊山
                 'http://travel.qunar.com/p-oi10010340-yilushan', #去哪儿伊芦山
                 'http://travel.qunar.com/p-oi10025389-chaohewanshengtaiyuan', #去哪儿潮河湾
                 'http://piao.qunar.com/ticket/detail_526407124.html?from=mpd_recommend_sight' # 去哪儿伊甸园
                 ]

    # 获取爬取程序实例
    newsGain = NewsGain()

    # 爬取数据
    for url in sourcetUrl:
        newsGain.startGain(url)

#    newsGain.inMysql(newsGain.data)
    newsGain.toCSV(newsGain.data)
#--------------------- 
#作者：大数据JavaLiu_Arvin 
#来源：CSDN 
#原文：https://blog.csdn.net/qq_36743482/article/details/80884933 
#版权声明：本文为博主原创文章，转载请附上博文链接！