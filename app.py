#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   app.py
@Time    :   2020/08/17 16:40:49
@Author  :   Du ShiKang 
@Version :   1.0
@Contact :   1103146395@qq.com
@Desc    :   None
'''

import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import time
class login(object):
    def __init__(self,user_info):
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
        }
        self.login_url='http://my.lzu.edu.cn:8080/login?service=http://my.lzu.edu.cn' 
        self.report_url='http://appservice.lzu.edu.cn/dailyReportAll/api/grtbMrsb/submit'
        self.st_url='http://my.lzu.edu.cn/api/getST'
        self.auth_url='http://appservice.lzu.edu.cn/dailyReportAll/api/auth/login'
        self.session=requests.Session()
        self.session.headers=self.headers
        self.name=user_info['name']
        self.username=user_info['username']
        self.password=user_info['password']
        self.xykh=user_info['xykh']
        self.province=user_info['province']
        self.city=user_info['city']
        self.area=user_info['area']
    def getLtAndCookie(self):
        response=self.session.get(url=self.login_url)
        html=response.text
        soup=BeautifulSoup(html,'lxml')
        LtInput=soup.find_all('input',type='hidden')[0]
        Lt=LtInput.attrs['value']
        return Lt
    def getLoginInformation(self):
        Lt=self.getLtAndCookie()
        formData={
            'username': self.username,
            'password': self.password,
            'lt': Lt,
            'execution': 'e1s1',
            '_eventId': 'submit'             
        }
        response=self.session.post(
            url=self.login_url,
            data=formData
        )
        print('{} 信息门户登录状态 {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),response.status_code))
        time.sleep(2)
        stResponse=self.session.post(
            url=self.st_url,
            data={'service': 'http://127.0.0.1'}
        )
        try:
            self.st=eval(stResponse.text)['data']
        except KeyError as ke:
            print('error:获取权限验证失败 {}'.format(ke))
            return -1
        time.sleep(2)
        authResponse=self.session.get(
            url='{}?st={}&PersonID={}'.format(self.auth_url,self.st,self.xykh)
        )
        self.user=eval(authResponse.text)
        print('{} 用户权限验证状态 {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),authResponse.status_code))
        time.sleep(2)
        return 0
    def autoKa(self):
        formData={
            'bh': 'ACB14B497C43A78BE053831510AC7612',
            'xykh': self.xykh,
            'twfw': '0',
            'sfzx': '0',
            'sfgl': '0',
            'szsf': self.province,
            'szds': self.city,
            'szxq': self.area,
            'sfcg': '0',
            'cgdd': '',
            'gldd': '',
            'jzyy': '',
            'bllb': '0',
            'sfjctr': '0',
            'jcrysm': '',
            'xgjcjlsj': '',
            'xgjcjldd': '',
            'xgjcjlsm': '',
            'zcwd': '0.0',
            'zwwd': '0.0',
            'wswd': '0.0',
            'sbr': self.name,
            'sjd': ''
        }
        response=self.session.post(
            url=self.report_url,
            data=formData,
            headers={
                'Authorization': self.user['data']['accessToken']
            }
        ) 
        print('{} 当前用户打卡状态 {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),response.text))
if __name__ =='__main__':
    user_info={
        'name':'杜世康', #姓名
        'username':' ', #信息门户登录邮箱名
        'password':' ', #信息门户登录密码
        'xykh':' ', #学号
        'province':'广东省', #打卡所在省
        'city':'广州市', #打卡所在市
        'area':'番禺区', #打卡所在区
        'clock_flag': False
    }

    def clock_job():
        clock=login(user_info)
        if clock.getLoginInformation()==0:
            clock.autoKa()
            user_info['clock_flag']=True
            message='{} 打卡成功~'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            message='{} 打卡失败~'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        requests.request(
            method='post',
            url='https://sc.ftqq.com/SCU62476T685cffHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH.send', #server酱微信消息推送，可选。此处应填自己的SRTKEY
            params={
                'text':'主人，您有新的打卡消息~',
                'desp': message
            }
        )
    def scheduler_job():
        print(user_info['clock_flag'])
        while not(user_info['clock_flag']):
            clock_job()
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduler_job, 'cron', day_of_week='1-7', hour=8, minute=30)
    # scheduler.add_job(scheduler_job, 'interval', seconds=5)
    scheduler.start()


