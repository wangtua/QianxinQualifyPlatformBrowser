# /usr/bin/env python3
# -*- coding=utf-8 -*-
# @Time : 2020/3/5
# @Author : wangtua


import requests
import logzero
import sys
import logging
import time
import random

from progressbar import ProgressBar
from logzero import logger
from lxml import etree

failed_urls = []
successed_urls = []

logzero.loglevel(logging.ERROR)
ClientUA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.34 Safari/537.36 Edg/81.0.416.20"

# set the log level of the process



def getLoginTokenCookie() -> str:
    headers = {'User-Agent' : ClientUA }
    login_page = requests.get("https://learning.b.qianxin.com/login/index.php",headers=headers)
    login_page_tree = etree.HTML(login_page.text)
    token = login_page_tree.xpath('/html/body/div/div[2]/div/section/div/div/div[1]/div/form/input[2]/@value')
    cookies = requests.utils.dict_from_cookiejar(login_page.cookies)
    #get cookies from cookiejar
    return (token,cookies)

def login(username:str,password:str,logintoken:str,cookies:dict) -> dict:
    headers = {'User-Agent' : ClientUA,'Origin':'https://learning.b.qianxin.com'}
    login_data = {"username":username,"password":password,"logintoken":logintoken,"anchor":""} # anchor is empty
    cookies = cookies
    logger.debug(login_data)
    logger.debug(cookies)
    res = requests.post("https://learning.b.qianxin.com/login/index.php",data=login_data,headers=headers,cookies=cookies, allow_redirects=False)
    cookies = requests.utils.dict_from_cookiejar(res.cookies)
    logger.debug(cookies)
    res = requests.get("https://learning.b.qianxin.com/login/index.php",headers=headers,cookies=cookies, allow_redirects=False)
    logger.debug(res.text)

    if "退出登录" in res.text:
        logger.info("login sucessed , session id:")
        print("\033[32mLOGIN SUCCESS \n")
    else:
        logger.error("login failed, please update the script")
        print("\033[31mLOGIN FAIL \n")
        sys.exit()

    return cookies

def browseLessonAll(lesson_list:list,lesson_href_list:list,cookies:dict):
   
    # the process is single-threaded temporarily.
    progress = ProgressBar()

    for href_id in progress(range(0,len(lesson_href_list))):
        time.sleep(random.randint(1,3))
        res = requests.get(lesson_href_list[href_id],cookies=cookies)
        #logger.debug(lesson_href_list[href_id]+" is finished")
        if 200 == res.status_code:
            successed_urls.append((lesson_list[href_id],lesson_href_list[href_id]))
        else:
            failed_urls.append((lesson_list[href_id],lesson_href_list[href_id]))

    msg  = "\033[m33BROWSE FINISHED!! the course contains {} lessons,  {} lessons succeeded and {} lessons failed.".format(len(successed_urls)+len(failed_urls)
                                                                                                    ,len(successed_urls)
                                                                                                    ,len(failed_urls))
    print(msg)   
    if failed_urls:
        print("\33[m31 THE FAILED URLS")
        for i in failed_urls:
            print(i)
    else:
        pass

def browseLessonsByLessonId(course_id:int,cookies:dict) -> tuple:
  
    url = "https://learning.b.qianxin.com/course/view.php?id="+str(course_id)

    logger.debug(cookies)
    res = requests.get(url,cookies=cookies)
    lessonContent = etree.HTML(res.text)
    
    lesson_list = lessonContent.xpath('/html/body/div/div/div/section/div/div/ul/li/div/ul/li/div/div/div[@class="activity-wrapper"]')
   
    if not lesson_list:
        logger.error("The lessonlist is missing, please update the xpath expression to the lessonlist !!!\n")
        sys.exit()  

    needBrowse = lambda element: 0 if len(element.xpath('div[@class="actions-right"]/span/span/img/@alt'))<=0 or "已完成" in element.xpath('div[@class="actions-right"]/span/span/img/@alt')[0] else 1
    filtered_list = list(filter(needBrowse,lesson_list))  

    getName = lambda element: element.xpath('div/a/span/text()')[0]
    lesson_name_list = list(map(getName,filtered_list))
    
    getHref = lambda element: element.xpath('div/a/@href')[0]
    lesson_href_list = list(map(getHref,filtered_list))
    
    
    msg = "\033[32m[+] THIS COURSE CONTAINS {} LESSONS IN TOTAL, AND YOU HAVE {} LESSONS LEFT TO BROWSE".format(len(lesson_list),len(lesson_name_list))
    print(msg)
   
    
  
    return (lesson_name_list,lesson_href_list,cookies)
    


def main():
    # step one:
    (token,login_cookies) = getLoginTokenCookie()
    if not token:
        # if can't get the token, exit the logging procedure
        logger.error("The login token is missing, please update the xpath expression to the token !!!\n")
        sys.exit()
    else:
        logger.debug("logintoken:"+token[0])
    # step two:
    print("\033[32m[+] PLEASE ENTER YOUR USERNAME: ")
    username = input()
    print("\033[32m[+] PLEASE ENTER YOUR PASSWORD: ")
    passwd = input()
    cookies = login(username,passwd,token[0],login_cookies)


    while True:
        print("                                       ")
        print("\033[0m[*] ------------MENU------------")
        print("[+] 1) BROWSE LESSONS BY COURSE ID ")
        print("[+] 2) OTHER FUNCTIONS IS DEVELOPING ")
        print("[+] 3) EXIT THE PROGRAM ")
        print(" \n")

        choice = int(input())
        if 1 == choice:
                print("PLEASE ENTER YOUR COURSE ID: ")
                print("\033[33m(COURSE ID is the number in the url) ")
                print("\033[0m ")
                course_id = input()
                (lesson_name_list,lesson_href_list,cookies) = browseLessonsByLessonId(course_id,cookies)
                browseLessonAll(lesson_name_list,lesson_href_list,cookies)

        elif 2 == choice:
                pass
        elif 3 == choice:
                sys.exit()
        else:
                print("PLEASE REENTER YOUR CHOICE!!")
       

  

if __name__=="__main__":
    main()