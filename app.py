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
import json
class login(object):
    def __init__(self,user_info):
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
        }
        self.login_url='http://my.lzu.edu.cn:8080/login?service=http://my.lzu.edu.cn' 
        self.report_url='http://appservice.lzu.edu.cn/dailyReportAll/api/grtbMrsb/submit'
        self.st_url='http://my.lzu.edu.cn/api/getST'
        self.auth_url='http://appservice.lzu.edu.cn/dailyReportAll/api/auth/login'
        self.md5_url='http://appservice.lzu.edu.cn/dailyReportAll/api/encryption/getMD5'
        self.info_url='http://appservice.lzu.edu.cn/dailyReportAll/api/grtbMrsb/getInfo'
        self.session=requests.Session()
        self.session.headers=self.headers
        self.username=user_info['username']
        self.password=user_info['password']
        self.xykh=user_info['xykh']
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
            return {'code':-1,'message':'权限验证失败'}
        time.sleep(2)
        authResponse=self.session.get(
            url='{}?st={}&PersonID={}'.format(self.auth_url,self.st,self.xykh)
        )
        self.user=eval(authResponse.text)
        print('{} 用户权限验证状态 {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),authResponse.status_code))
        md5Rsponse=self.session.post(
            url=self.md5_url,
            data={'cardId':self.xykh},
            headers={
                'Authorization': self.user['data']['accessToken']
            }
        )
        try:
            self.md5=eval(md5Rsponse.text)['data']
        except KeyError as ke:
            print('error:获取密钥失败 {}'.format(ke))
            return {'code':-1,'message':'获取密钥失败'}
        infoResponse=self.session.post(
            url=self.info_url,
            data={
                'cardId':self.xykh,
                'md5':self.md5
            },
            headers={
                'Authorization': self.user['data']['accessToken']
            }
        )
        try:
            infoText=json.loads(infoResponse.text)
            self.bh=infoText['data']['list'][0]['bh']
            self.xm=infoText['data']['list'][0]['xm']
            self.szsf=infoText['data']['list'][0]['szsf']
            self.szds=infoText['data']['list'][0]['szds']
            self.szxq=infoText['data']['list'][0]['szxq']
            self.sbr=infoText['data']['list'][0]['sbr']
        except KeyError as ke:
            print('error:获取用户信息失败 {}'.format(ke))
            return {'code':-1,'message':'获取用户信息失败'}
        print('{} 用户信息获取状态 {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),infoResponse.status_code))
        time.sleep(2)
        return {'code':1,'message':'成功获取用户登录信息'}
    def autoKa(self):
        formData={
            'bh': self.bh,
            'xykh': self.xykh,
            'twfw': '0',
            'sfzx': '0',
            'sfgl': '0',
            'szsf': self.szsf,
            'szds': self.szds,
            'szxq': self.szxq,
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
            'sbr': self.sbr,
            'sjd': ''
        }
        response=self.session.post(
            url=self.report_url,
            data=formData,
            headers={
                'Authorization': self.user['data']['accessToken']
            }
        ) 
        print('{} 用户打卡返回信息 {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),response.text))
if __name__ =='__main__':
    user_info={
        'username':'xxxx',     #信息门户登录邮箱名 xxxx@lzu.edu.cn
        'password':'password', #信息门户登录密码  password
        'xykh':'22019xxxxxxx', #校园卡号         22019xxxxxxx
    }
    def clock_job(flag):
        clock=login(user_info)
        login_status=clock.getLoginInformation()
        if login_status['code']==1:
            clock.autoKa()
            flag=True
            message='{} 打卡成功~'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            flag=False
            message='{} 打卡失败，失败信息{}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),login_status)
        requests.request(
            method='post',
            url='https://sc.ftqq.com/SCU62476T685cff44078a2f6021c6xxxxxxxxxxxxxxxxxxxxxxxxxx.send', #server酱微信消息推送，可选。此处应填自己的SRTKEY
            params={
                'text':'主人，您有新的打卡消息~',
                'desp': message
            }
        )
        return flag
    def scheduler_job():
        flag=False
        while not(flag):
            flag=clock_job(flag)
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduler_job, 'cron', day_of_week='0-6', hour=9, minute=00)
    # scheduler.add_job(scheduler_job, 'interval', seconds=5)
    scheduler.start()


