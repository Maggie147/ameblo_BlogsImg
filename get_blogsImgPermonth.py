#!/usr/bin/python python
# -*- coding: utf-8 -*-
"""
__title__ = 'python_2.7 [requests] get blog image v1.0'
__author__ = 'xxxx'
__mtime__ = '2017-11-03'

"""

import os
import sys
import pprint
import requests
import time
import re
from requests import Request, Session
from multiprocessing.dummy import Pool
# sys.path.append("../Common/pylib")
reload(sys)
sys.setdefaultencoding('utf8')
total_img_num = 0

photo_folder = ''

def usage(processName):
    print "Usage: %s URL  Path" % processName
    print "For example:"
    print "     ..."

def check_input(buf):
    if not buf:
        print "Not input blog time"
        sys.exit()
    try:
        int(buf)
    except Exception as e:
        print "Please ckeck up input[eg: 201710]"
        sys.exit()
    strLen = len(buf.strip())
    if strLen == 5:
        time = buf[:4] + '0'+ buf[-1]
    elif strLen == 6:
        time = buf
    else:
        print "Please ckeck up input[eg: 201710]"
        sys.exit()
    return time

def get_nowtime(tStamp=1):
    '''tStamp is 1, return now time by timeStamp.'''
    if tStamp == 1:
        timeStamp = time.time()
        return timeStamp
    else:
        time_local  = time.localtime()
        YMD = time.strftime("%Y-%m-%d", time_local)
        return YMD

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
        print "HTTP error, status_code is %s,  url=%s"%(response.status_code, url)
        return None
    if debug:
        print url
        print response.status_code
        pprint.pprint(headers) 

    if filename:
        with open(filename, 'wb') as fd:
            for response_data in response.iter_content(1024):
                fd.write(response_data)
        return filename             
    else:
        return response.text 

def download_img(url):
    try:
        img_src = url
        name_p = img_src.rfind('/')
        name_p2 = img_src.rfind('.jpg')
        img_name = img_src[name_p+1:name_p2+4]
        img_path = photo_folder.strip() + img_name.strip()
        # print img_name
        filename = GetMsgEx(img_src.strip(), filename=img_path)
        if not filename:
            print "get img_src[%s] failed!"%img_src
            return None 
        return filename
    except Exception as e:
        print e
        return None

def get_blogTT(buf):
    restr = r'data-unique-entry-title="(.*?)"'    
    ret = re.findall(restr, buf, re.S | re.M)
    title = ''
    if ret:
        title = ret[0].decode('utf-8')
    restr = r'<span class="articleTime.*?<time.*?>(.*?)</time>'    
    ret2 = re.findall(restr, buf, re.S | re.M)
    time = ''
    if ret2:
        time = ret2[0]
    return (title, time)

def get_imgsSrc(buf):
    img_urls = []
    restr = r'<div class="articleText"(.*?)</div>'
    ret = re.findall(restr, buf, re.S | re.M)
    if ret:
        restr = r'<a id=".*?class="detailOn".*?<img.*?src="(.*?)"'
        img_list = re.findall(restr, str(ret), re.S | re.M)
        img_urls = [img for img in img_list if img]
    return img_urls


def get_allBlogs(first_url, debug):
    if not first_url:
        print "NO url to request!"
        return None
    headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Upgrade-Insecure-Requests': '1'}
    response = GetMsgEx(first_url, headers)
    if not response:
        print "request first_url[%s] error!" % first_url
        return None

    blogs_urls = []
    restr = r'<ul class="contentsList skinBorderList">(.*?)</ul>'
    ret = re.findall(restr, response, re.S | re.M)
    # pattern = re.compile(restr,re.VERBOSE | re.IGNORECASE |re.DOTALL)
    # ret  = pattern.findall(response)
    # print ret
    if ret:
        restr = r'<li>.*?<a class="contentTitle" href="(.*?)">'
        blogs_list = re.findall(restr, str(ret), re.S | re.M)
        blogs_urls = [blog for blog in blogs_list if blog]
    return blogs_urls


def analyse_blogs(argv):
    global total_img_num
    blog_url = argv[0]
    debug   = argv[1]
    response = GetMsgEx(blog_url.strip())
    if not response:
        print "request blog_url[%s] faild!" % blog_url
        return (None,None,None)
    blog_title = blog_time = ''
    blog_title, blog_time =  get_blogTT(response)
    print "blog_title: ", blog_title
    print "blog_time:  ", blog_time

    print "get img src, and dowmload..."
    imgs_src = get_imgsSrc(response)
    if imgs_src:
        imgs_num = len(imgs_src)
        print "this blog img_num: %d\n"%imgs_num
        total_img_num = total_img_num + imgs_num
        pool = Pool(len(imgs_src))
        filenames = pool.map(download_img, imgs_src)
        pool.close()
        pool.join()
        for per in filenames:
            if per:
                # print "download %s successful!"% per
                pass
            else:
                print "download %s failed!!!!!"%per
        return (blog_title, blog_time, len(imgs_src))


def start_fun(para, debug=0):
    global photo_folder
    time_start = get_nowtime()
    try:
        first_url = para['URL'].strip()
        photo_folder  = para['Path'].strip()
    except Exception as e:
        print e
        sys.exit()

    ''' get all blogs list'''
    print "get blogs url list..."
    blogs_urls = get_allBlogs(first_url, debug)
    if not blogs_urls or not isinstance(blogs_urls, list):
        print "get  blogs url failed!!!"
        sys.exit()

    ''' Pool analyse blogs list'''
    total_blog_num = len(blogs_urls)
    print "total blogs_num: ", total_blog_num
    debugs = [debug]*total_blog_num
    pool = Pool(total_blog_num)
    pool.map(analyse_blogs, zip(blogs_urls, debugs))
    pool.close()
    pool.join()

    time_end = get_nowtime()
    print "total_blog_num: ", total_blog_num
    print "total_img_num:  ", total_img_num
    print "Lasted %d seconds" % (time_end-time_start)


def main():
    para = {}
    argc = len(sys.argv)
    if argc == 1:
        inputString = raw_input("Enter request blog_time year month [eg: 201710]: ")
        blog_time = check_input(inputString)
        para['URL']  = "https://ameblo.jp/officialpress/archiveentrylist-%s.html"%blog_time
        para['Path'] = "./"+str(blog_time)+"/"
    elif argc == 3:
        para['URL'] = sys.argv[1]
        para['Path'] = sys.argv[2]
    else:
        usage(sys.argv[0])
        sys.exit(-1)

    ''' make sure pic path is ok'''     
    if not os.path.exists(para['Path']):
        os.makedirs(para['Path'])

    if not para['URL'] or not para['Path']:
        sys.exit()

    debug = 0
    start_fun(para, debug)


if __name__ == "__main__":
    main()