# -*- coding: UTF-8 -*-
"""
__title__ = 'python3 [requests] get blog image v2.0'
__author__ = 'xxxx'
__ctime__ = '2017-11-03'
__mtime__ = '2018-04-10'

"""
import os
import sys
import pprint
import requests
import time
import re
from requests import Request, Session
from multiprocessing.dummy import Pool


class HandleWithinput():
    def __init__(self, debug):
        self.debug = debug
        self.raw_url = ''
        self.save_path = ''
        self.__argcCheck()

    def __argcCheck(self):
        if len(sys.argv) == 1:
            rawInput = input("Enter request blog_time year month [eg: 201710]: ")   # python3 no raw_input()
            valInput = self.__isValid(rawInput)
            self.raw_url = "https://ameblo.jp/officialpress/archiveentrylist-{}.html".format(valInput)
            self.save_path = './' + str(valInput) + '/'
        elif len(sys.argv) == 3:
            self.raw_url = sys.argv[1].strip()
            self.save_path = sys.argv[2].strip()
        else:
            self.__usage(sys.argv[0])
            sys.exit(-1)

    def __isValid(self, buf):
        try:
            int(buf)
        except Exception as e:
            print("Please ckeck up input blog_time, include year month[eg: 201710]")
            sys.exit()
        buflen = len(buf.strip())
        if buflen == 5:
            result = buf[:4] + '0'+ buf[-1]
        elif buflen == 6:
            result = buf
        else:
            print("Please ckeck up input[eg: 201710]")
            sys.exit()
        return result

    def __usage(self, processName):
        print("Usage: {} URL  Path".format(processName))
        print("For example:")
        print("     ...")

    def myPrint(self):
        print("debug    : ", self.debug )
        print("raw_url  : ", self.raw_url)
        print("save_path: ", self.save_path)



def GetMsgEx(url, para=None, cookies=None, data=None, filename=None, debug=0):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    if para:
        for key in para.keys():
            if para[key] is None:
                del para[key]
            else:
                if key == 'User-Agent' and para['User-Agent'] != '':
                    headers['User-Agent'] = para['User-Agent']
                else:
                    headers[key] = para[key]
    if cookies and len(cookies) != 0:
        headers['cookie'] = cookies
    try:
        if not data or len(data) == 0:
            response = requests.get(url, headers=headers)
        else:
            response = response.post(url, headers=headers, data=data)
    except Exception as e:
        raise e
        return None
    if str(response.status_code)[0] != '2':
        print( "HTTP error, status_code is %s,  url=%s"%(response.status_code, url))
        return None
    if debug:
        print(url)
        print(response.status_code)
        pprint.pprint(headers)

    if filename:
        with open(filename, 'wb') as fd:
            for response_data in response.iter_content(1024):
                fd.write(response_data)
        return filename
    else:
        return response.text


class amebloImg():
    def __init__(self, para):
        self.__paraCheck(para)
        self.blogNum = 0
        self.imagNum = 0
        self.imagUrl = []

    def __paraCheck(self, para):
        if not para.raw_url or not para.save_path:
            sys.exit()
        try:
            self.debug = para.debug
            self.first_url = para.raw_url.strip()
            self.photo_folder = para.save_path.strip()
        except Exception as e:
            print(e)
            sys.exit()

    def blogslistGet(self):
        blogs_urls = []

        headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Upgrade-Insecure-Requests': '1'}

        try:
            response = GetMsgEx(self.first_url, headers)
            if not response:
                print("request first_url[ {}] error!".format(self.first_url))
                return None
            # print(response.encode('utf-8'))

            restr = r'<ul.*?class="skin-archiveList">(.*?)</ul>'
            ret = re.findall(restr, response, re.S | re.M)
            # pattern = re.compile(restr,re.VERBOSE | re.IGNORECASE |re.DOTALL)
            # ret  = pattern.findall(response)
            # print ret
            if ret:
                restr = r'<li.*?<a href="(.*?)">'
                blogs_list = re.findall(restr, str(ret), re.S | re.M)
                blogs_urls = [blog.strip() for blog in blogs_list if blog]
        except Exception as e:
            print(e)
        self.blogNum = len(blogs_urls)
        return blogs_urls

    def blogAnalyse(self, blogUrl):
        response = GetMsgEx(blogUrl.strip())
        if not response:
            print("request blog_url[ {} ] faild!".format(blogUrl))
            # return (None,None,None)

        # get blog title, time

        # get blogImg
        imgsList = self.__imagUrlGet(response)
        if not imgsList:
            print("not get img url, blog url: ", blogUrl)
        else:
            self.imagNum += len(imgsList)
            self.imagUrl.extend(imgsList)

    def __imagUrlGet(self, buf):
        img_urls = []
        restr = r'<div.*?id="entryBody"(.*?)</div>'
        ret = re.findall(restr, buf, re.S | re.M)
        if ret:
            restr = r'<a.*?<img.*?src="(.*?)"'
            img_list = re.findall(restr, str(ret), re.S | re.M)
            img_urls = [img.strip() for img in img_list if img]
        return img_urls

    def imagDownload(self, url):
        try:
            urltmp = url
            urltmp = urltmp.split('/')[-1]
            imgName = urltmp.split('?')[0]
            # print("imgName: ", imgName)

            img_path = self.photo_folder.strip() + imgName.strip()
            # print img_name
            filename = GetMsgEx(url.strip(), filename=img_path)
            if not filename:
                print("get img_src[%s] failed!"%img_src) 
                return None 
            return filename
        except Exception as e:
            print(e)
            return None

    def myPrint(self):
        print("debug    : ", self.debug )
        print("raw_url  : ", self.first_url)
        print("save_path: ", self.photo_folder)

        print("total blogNum: ", self.blogNum)
        print("total imagNum: ", self.imagNum)
        print("total imagNum: ", len(self.imagUrl))


def main():
    debug = 1
    para = HandleWithinput(debug)

    ameba = amebloImg(para)

    # get blog list
    blogList = ameba.blogslistGet()
    if not blogList:
        print("get  blogs url list failed!!!")
        sys.exit()

    # Analyse blog
    pool = Pool(20)
    results = pool.map(ameba.blogAnalyse, blogList)    # results = pool.map(self.__blogAnalyse, zip(blogList, ))
    pool.close()
    pool.join()

    # download img
    pool = Pool(20)
    results = pool.map(ameba.imagDownload, ameba.imagUrl)
    pool.close()
    pool.join()
    for item in results:
        if not item:
            print("Download {} failed!!!!!!".format(item))

if __name__ == '__main__':
    main()