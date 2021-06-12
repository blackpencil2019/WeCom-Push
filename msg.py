#coding:utf-8
'''
@author: blackpencil2019
@LastEditors: blackpencil2019
@description: 企业微信消息推送
@Date: 2021-06-12
'''
import requests
import json
from configparser import ConfigParser
import time

class WeComPush:
    '企业微信消息推送'
    api_access_token = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    api_push_msg = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
    
    def __init__(self, corpID="", appID="", appSecret=""):
        config = ConfigParser()
        config.read('user.config', encoding='UTF-8-sig')
        if corpID == "":
            self.corpID = config['setting']['ENTERPRISE_ID']
        else:
            self.corpID = corpID
        if appID == "":
            self.agentID = config['setting']['APP_ID']
        else:
            self.agentID = appID
        if appSecret == "":
            self.appSecret = config['setting']['APP_SECRET']
        else:
            self.appSecret = appSecret
        
        # 初始化token
        try:
            with open('token.json','r') as fileToken:
                # 使用json读取cookies 注意读取的是文件 所以用load而不是loads
                savedResult = json.load(fileToken)
        except:
            savedResult = {"access_token":"", "timestamp":0, "expires_in":0}
        self.acessToken = savedResult["access_token"]
        self.lastUpdateTime = savedResult["timestamp"]
        self.expires = savedResult["expires_in"]
    
    # 请求acess_token
    def getAcessToken(self):
        acessParams = {
            'corpid': self.corpID,
            'corpsecret': self.appSecret
        }
        req = requests.get(self.api_access_token, params = acessParams)
        # 请求成功 
        if req.status_code == 200:
            result = json.loads(req.text)
            if result["errcode"] == 0:
                self.acessToken = result["access_token"]
                self.expires = result["expires_in"]
                timeStamp = int(time.time())
                self.lastUpdateTime = timeStamp
                result["timestamp"] = timeStamp
                # 保存到文件
                with open('token.json','w') as fileToken:
                    fileToken.write(json.dumps(result))
                # print(self.acessToken, self.expires, self.lastUpdateTime)
                return True
            else:
                print("Get AcessToken failed!(" + str(result["errcode"]) + ": " + result["errmsg"] + ")")
        # 请求失败       
        if req.status_code == 404:
            print("Request for AcessToken failed!")
            return False
        # 其他请求错误
        print("ErrorCode: "+req.status_code+". Request for AcessToken failed!")   
        return False
    
    
    def send(self, msgData):   
        currentTime = int(time.time())
        # print(currentTime)
        # 判断token是否失效
        if currentTime - self.lastUpdateTime >= self.expires-5:
            if False == self.getAcessToken():    # 获取token失败
                return False
                
        msgParams = {
            "access_token" : self.acessToken
        }
        
        # 尝试发送数据
        req = requests.post(self.api_push_msg, params = msgParams, data = json.dumps(msgData))
        # 请求成功
        if req.status_code == 200:

            result = json.loads(req.text)
            
            if 0 == result["errcode"]:  # 发送成功
                print("Send msg succeed.")
                return True
                
            elif 42001 == result["errcode"]:   # token失效导致，重新发送一次
                if self.getAcessToken():
                
                    msgParams = {
                        "access_token" : self.acessToken
                    }
                    
                    req2 = requests.post(self.api_push_msg, params = msgParams, data = json.dumps(msgData))
                    result2 = json.loads(req2.text)
                    
                    if 0 == result2["errcode"]: # 获取新的token后发送成功
                        print("Get new AcessToken and send msg succeed.")
                        return True
            # 发送消息失败     
            print("Send Message failed!(" + str(result["errcode"]) + ": " + result["errmsg"] + ")")
        # 请求失败    
        else:
            print("ErrorCode: "+req.status_code+". Request for sending msg failed!")
        
        return False
        
        
    # 普通消息
    def pushMsg(self, msgContent, usr="@all", party = "", tag = ""):
        msgData = {
           "touser" : usr, # 指定接收消息的成员, 指定为”@all”，则向该企业应用的全部成员发送
           "toparty" : party, # 指定接收消息的部门, 多个接收者用‘|’分隔, 当touser为”@all”时忽略本参数
           "totag" : tag, # 指定接收消息的标签, 当touser为”@all”时忽略本参数
           "msgtype" : "text",
           "agentid" : self.agentID,  # 企业微信应用ID
           "text" : {
               "content" : msgContent
           },
           "safe":0,
           "enable_id_trans": 0,    # 开启转义，企业自建应用可以忽略
           "enable_duplicate_check": 1, # 表示是否开启重复消息检查
           "duplicate_check_interval": 30   #表示是否重复消息检查的时间间隔
        }       
        
        return self.send(msgData)
    
    
    # 卡片消息
    def pushCardMsg(self, title, desc = "", url = "https://work.weixin.qq.com/api/doc/90000/90135/90236", 
                          usr = "@all", party = "", tag = ""):
        timeStamp = time.strftime("%Y{y}%m{m}%d{d} %H:%M:%S", time.localtime()).format(y='年', m='月', d='日')
        cardData = {
           "touser" : usr, # 指定接收消息的成员, 指定为”@all”，则向该企业应用的全部成员发送
           "toparty" : party, # 指定接收消息的部门, 多个接收者用‘|’分隔, 当touser为”@all”时忽略本参数
           "totag" : tag, # 指定接收消息的标签, 当touser为”@all”时忽略本参数
           "msgtype" : "textcard",
           "agentid" : self.agentID,
           "textcard" : {
                "title" : title,
                "description" : "<div class=\"gray\">" + timeStamp + "</div><br><div class=\"normal\">" + desc + "</div>",
                "url" : url,    # 点击卡片跳转链接
                "btntxt":""     # 底部显示文本，默认"详情"
           },
           "enable_id_trans": 0,    # 开启转义，企业自建应用可以忽略
           "enable_duplicate_check": 1, # 表示是否开启重复消息检查
           "duplicate_check_interval": 30   #表示是否重复消息检查的时间间隔
        }
        return self.send(cardData)
