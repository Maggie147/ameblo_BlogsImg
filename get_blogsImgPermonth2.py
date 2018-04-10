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


class DealWithArgv():
    def __init__(self, debug):
        self.debug = debug
        self.raw_url = ''
        self.save_path = ''
        self.__argvCheck()

    def __argvCheck(self):
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
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

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


class AmebloImgReq():
    def __init__(self, para):
        self.__paraGet(para)
        self.img_url = []
        self.blog_num = 0
        self.imag_num = 0
        self.imag_faild = 0


    def __paraGet(self, para):
        if not para.raw_url or not para.save_path:
            sys.exit()
        try:
            self.debug = para.debug
            self.img_dir = para.save_path.strip()
            self.ent_url = para.raw_url.strip()
        except Exception as e:
            print(e)
            sys.exit()

    def GetMsgEx(self, url, para=None, cookies=None, data=None, filename=None):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        if para:
            for key in para.keys():
                if para[key] is None:
                    del para[key]
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
            print(e)
            return None
        if str(response.status_code)[0] != '2':
            print( "HTTP error, status_code is %s,  url=%s"%(response.status_code, url))
            return None
        if self.debug:
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

    def bloglistGet(self):
        headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Upgrade-Insecure-Requests': '1'}
        response = self.GetMsgEx(self.ent_url, para = headers)
        if not response:
            print("request enter_url [{}] error!".format(self.ent_url))
            return None

        try:
            blogs = []
            restr = r'<ul.*?class="skin-archiveList">(.*?)</ul>'
            ret = re.findall(restr, response, re.S | re.M)
            # pattern = re.compile(restr,re.VERBOSE | re.IGNORECASE |re.DOTALL)
            # ret  = pattern.findall(response)
            if not ret:
                print("get bloglist html body failed!!")
                return None
            restr = r'<li.*?<a href="(.*?)">'
            bloglist = re.findall(restr, str(ret), re.S | re.M)
            blogs = [item.strip() for item in bloglist if item]
        except Exception as e:
            print(e)
        self.blog_num = len(blogs)
        return blogs

    def blogAnalyse(self, url):
        response = self.GetMsgEx(url.strip())
        if not response:
            print("request blog [{}] faild!".format(url))
            return None

        # get blog title, time

        # get blogImg
        imgsList = self.__imagUrlGet(response)
        if not imgsList:
            print("get imag list faild!!!, raw blog url: ", url)
            return None
        self.imag_num += len(imgsList)
        self.img_url.extend(imgsList)

    def __imagUrlGet(self, buf):
        try:
            imgs = []
            restr = r'<div.*?id="entryBody"(.*?)</div>'
            ret = re.findall(restr, buf, re.S | re.M)
            if not ret:
                print("get blog html img body failed!!!")
                return None
            restr = r'<a.*?<img.*?src="(.*?)"'
            imglist = re.findall(restr, str(ret), re.S | re.M)
            imgs = [img.strip() for img in imglist if img]
        except Exception as e:
            print(e)
        return imgs


    def imgDownload(self, url):
        try:
            urltmp = url
            urltmp = urltmp.split('/')[-1]
            imgName = urltmp.split('?')[0]

            img_path = self.img_dir.strip() + imgName.strip()
            filename = self.GetMsgEx(url.strip(), filename=img_path)
            if not filename:
                print("get img_src[%s] failed!" % url)
                self.imag_faild += 1
                return None
            return filename
        except Exception as e:
            print(e)
            return None

    def myPrint(self):
        print("debug  : ", self.debug )
        print("ent_url: ", self.ent_url)
        print("img_dir: ", self.img_dir)

        print("total blog_num: ", self.blog_num)
        print("total imag_num: ", self.imag_num)
        print("total imag_num: ", len(self.img_url))
        print("faild imag_num: ", self.imag_faild)


def main():
    debug = 0
    para = DealWithArgv(debug)

    ameba = AmebloImgReq(para)

    # get blog list
    blogList = ameba.bloglistGet()
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
    results = pool.map(ameba.imgDownload, ameba.img_url)
    pool.close()
    pool.join()
    for item in results:
        if not item:
            print("Download {} failed!!!!!!".format(item))
    ameba.myPrint()


if __name__ == '__main__':
    main()