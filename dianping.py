# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 23:33:13 2018

@author: Administrator
"""

#coding=utf-8
from bs4 import BeautifulSoup
import requests
import sys
stdi,stdo,stde=sys.stdin,sys.stdout,sys.stderr
#reload(sys) 
sys.stdin,sys.stdout,sys.stderr=stdi,stdo,stde
#sys.setdefaultencoding("utf-8")
import json

#cfgcookie.txt人工输入的cookie
def getcookiestr(path):
    '''
    path:配置文件路径
    '''
    try:
        dicookie = {}
        with open(path + r'cfgcookie.txt', 'r') as r:
            inputstr = r.read()
            for one in inputstr.split('; '):
                dicookie[one.split('=')[0]] = one.split('=')[1]
        #    for x,y in dicookie.items():
        #        print (type(y))
        print(dicookie)
        return dicookie
    except Exception as e:
        print (str(e))
        print (u'请检查cfgcookie.txt配置文件正确性！')

#cfgcookie.txt人工输入的cookie    
#newcookie.json记录每次操作后更新的cookie
def getcookies(path):
    '''
    path:配置文件路径
    '''
    try:
        dicookie = {}
        with open(path + r'newcookie.json','r') as r:
            try:
                dicookie = json.load(r)
                print (dicookie)
            except Exception as e:
                print (str(e))
                #newcookie.json读取错误之后读取cfgcookie.txt
                with open(path + r'cfgcookie.txt', 'r') as r:
                    inputstr = r.read()
                    for one in inputstr.split('; '):
                        dicookie[one.split('=')[0]] = one.split('=')[1]
                #    for x,y in dicookie.items():
                #        print (type(y))
        return dicookie
    except Exception as e:
        print (str(e))
        print (u'请检查cfgcookie.txt配置文件正确性！')

def savenewcookie(path, dicookie):
    '''
    存储最新的cookie
    path:配置文件路径
    dicookie:存储的dict
    '''
    try:
        with open(path + r'newcookie.json','w') as w:
            json.dump(dicookie,w)
    except Exception as e:
        print (str(e))
        print (u'存储newcookie.json出错了！')

def get_dianping(scenic_url):
    proxies = {
#    "http": "50.233.137.33:80",
    "http":"218.59.139.238:80",
    }
    headers = {
        'Host': 'www.dianping.com',
        'Referer': 'http://www.dianping.com/shop/22711693',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/535.19',
        'Accept-Encoding': 'gzip'
    }
    headers['Referer'] = scenic_url.replace('https', 'http').replace('/review_all', '')
#    cookies = {'cy':'835', 
#                   'cye':'guanyun', 
#                   '_lxsdk_cuid':'16426247fafc8-0cf040f6fc4a118-4c312b7b-100200-16426247fafc8',
#                   '_lxsdk':'16426247fafc8-0cf040f6fc4a118-4c312b7b-100200-16426247fafc8',
#                   '_hc.v':'7b5b3de6-776c-46d2-e7d3-e468d13446dc.1529648284',
#                   '_dp.ac.v':'c584c92c-95aa-4220-a4e0-bb40878ae863',
#                   'ua':'15366181451',
#                   's_ViewType':'10', 
#                   '_lxsdk_s':'1644ec042ce-f7f-0ee-489%7C%7C1176',
#                   'cityInfo':'%7B%22cityId%22%3A835%2C%22cityEnName%22%3A%22guanyun%22%2C%22cityName%22%3A%22%E7%81%8C%E4%BA%91%E5%8E%BF%22%7D',
#                   '__mta':'146585483.1530329665619.1530330562343.1530330863738.6',
#                   'ctu':'4a3974cdf5b2e5b0fd3b2d9a6ec23a7d48c74ae4f2a36e72bfed34b59b322f331e42d186b52cd0db5fa5a045e40f22d4',
#                   'dper':'79ff66a7e0fc79b70c8ac58013ca79eda9a3b87d62b5ad42a670e8244ddcbba0ee1a751db6a8e0ff39608623d5575eb1e6f8237e50713a9455f35c1d81ef75cbed81c68fc95315a4c2dde5930e0a840d14eddc61aee31c213f59c602aba3d13d',
#                   'll':'7fd06e815b796be3df069dec7836c3df',
#                   '_lx_utm':'utm_source%3DBaidu%26utm_medium%3Dorgani'}
    # 之前的cookie已过期
    cookies = {'cy':'835', 
                   'cye':'guanyun', 
                   '_lxsdk_cuid':'165326abb16c8-0b4257bdbfb683-4c312b7b-144000-165326abb17c8',
                   '_lxsdk':'165326abb16c8-0b4257bdbfb683-4c312b7b-144000-165326abb17c8',
                   '_hc.v':'f342b8f4-76bd-b7e3-f311-dde38460f6a9.1534149181',
                   'ua':'15366181451',
                   '_lxsdk_s':'16532c04c62-0a1-332-21f||51',
                   'ctu':'984140a059b7ea17dc9cf8a1beabdc7a327e77fb491f3f781040b77efe2e8459',
                   'dper':'79ff66a7e0fc79b70c8ac58013ca79ed63f150e8da4061cd8c570a3e17266cfad5d17e745b95f2276ca66f1c978ffe8e7c12c3e228110081542c4a8ebd9518951784feb7aa8b609eec66fc66f67c483cb7fb7f1c56f991490523848b82b003ec',
                   'll':'7fd06e815b796be3df069dec7836c3df'}

#    cookies= getcookiestr('.\\')

#    cookies = {,
#        '_lxsdk_cuid': '16146a366a7c8-08cd0a57dad51b-32637402-fa000-16146a366a7c8',
#        '_lxsdk': '16146a366a7c8-08cd0a57dad51b-32637402-fa000-16146a366a7c8',
#        '_hc.v': 'ec20d90c-0104-0677-bf24-391bdf00e2d4.1517308569',
#        's_ViewType': '10',
#        'cy': '16',
#        'cye': 'wuhan',
#        '_lx_utm': 'utm_source%3DBaidu%26utm_medium%3Dorganic',
#        '_lxsdk_s': '1614abc132e-f84-b9c-2bc%7C%7C34'
#    }
    requests.adapters.DEFAULT_RETRIES = 5
    s = requests.session()
    s.keep_alive = False

    returnList = []
#    url = "https://www.dianping.com/shop/%s/review_all" % scenic_id
    r = requests.get(scenic_url, headers=headers, cookies=cookies, proxies = proxies)#
#    print r.text

    with open(r'downloade0.html','wb') as w:
            w.write(r.text.encode('utf-8'))
    soup = BeautifulSoup(r.text, 'lxml')
#    print soup
    lenth = soup.find_all(class_='PageLink').__len__() + 1
    print ("lenth:%d"%(lenth))

    title = soup.select_one('.shop-name')
    try:
        title = title.get_text()
    except Exception as e:
        pass
    print ("title:%s"%(title))
    coment = soup.select('.reviews-items ul li')

    for one in coment:
        try:
            if one['class'][0]=='item':
                continue
        except Exception:
            pass
        time = one.select_one('.main-review .time')
        time = time.get_text().strip()
        print ("time:%s"%(time))
        name = one.select_one('.main-review .dper-info .name')
        name = name.get_text().strip()
        print ("name:%s"%(name))
        star = one.select_one('.main-review .review-rank span')
        star = star['class'][1][7:8]
        print ("star:%s"%(star))
        pl = one.select_one('.main-review .review-words')
        words = pl.get_text().strip().replace(u'展开评论','')
        print ("word:%s"%(words))
        returnList.append([title,time,name,words,star])
        print ('=============================================================')
    if lenth > 1:
        headers['Referer'] = scenic_url.replace('https', 'http')
        for i in range(2,lenth+1):
            urlin = scenic_url + '/p' + str(i)
            r = requests.get(urlin, headers=headers, cookies=cookies, proxies = proxies)
            with open(r'downloade.html','wb') as w:
                w.write(r.text.encode('utf-8'))
#            print r.text
            soup = BeautifulSoup(r.text, 'lxml')
            title = soup.select_one('.shop-name')
            title = title.get_text()
            print ("title:%s"%(title))
            coment = soup.select('.reviews-items ul li')

            for one in coment:
                try:
                    if one['class'][0]=='item':
                        continue
                except Exception:
                    pass
                time = one.select_one('.main-review .time')
                time = time.get_text().strip()
                print ("time:%s"%(time))
                name = one.select_one('.main-review .dper-info .name')
                name = name.get_text().strip()
                print ("name:%s"%(name))
                star = one.select_one('.main-review .review-rank span')
                star = star['class'][1][7:8]
                print ("star:%s"%(star))
                pl = one.select_one('.main-review .review-words')
                words = pl.get_text().strip().replace(u'展开评论','').replace(u'收起评论','')
                print ("word:%s"%(words))
                returnList.append([title,time,name,words,star])
                print ('=============================================================')
    return returnList

def atest():
    headers = {
        'Host': 'www.baidu.com',
        'Referer': 'https://www.baidu.com/link?url…6885dc00070b51000000035b3765f4',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/535.19',
        'Accept-Encoding': 'gzip'
    }
    cookies= getcookiestr('.\\')
    cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
    resion = requests.Session()
    resion.cookies = cookies
    r = resion.get('https://www.baidu.com/', headers=headers)
    savenewcookie('.\\', r.cookies.get_dict())#存储更新后的cookie

if __name__ == "__main__":
    get_dianping('https://www.dianping.com/shop/5400289/review_all')
#    atest()
#--------------------- 
#作者：大数据JavaLiu_Arvin 
#来源：CSDN 
#原文：https://blog.csdn.net/qq_36743482/article/details/80884933 
#版权声明：本文为博主原创文章，转载请附上博文链接！