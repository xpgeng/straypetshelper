# -*- coding: utf-8 -*-
'''
Project: SPH-wechat
Author: Shenlang
'''

import sys,requests
import sae.kvdb
import time
import xml.etree.ElementTree as ET
reload(sys)
sys.setdefaultencoding('utf-8')


textTpl = """<xml>
        <ToUserName><![CDATA[%s]]></ToUserName>
        <FromUserName><![CDATA[%s]]></FromUserName>
        <CreateTime>%s</CreateTime>
        <MsgType><![CDATA[%s]]></MsgType>
        <Content><![CDATA[%s]]></Content>
        </xml>"""

textTpl_image = """<xml>
        <ToUserName><![CDATA[%s]]></ToUserName>
        <FromUserName><![CDATA[%s]]></FromUserName>
        <CreateTime>%s</CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>2</ArticleCount>
        <Articles>
        <item>
        <Title><![CDATA[%s]]></Title> 
        <Description><![CDATA[%s]]></Description>
        <PicUrl><![CDATA[%s]]></PicUrl>
        <Url><![CDATA[%s]]></Url>
        </item>
        <item>
        <Title><![CDATA[%s]]></Title>
        <Description><![CDATA[%s]]></Description>
        <PicUrl><![CDATA[%s]]></PicUrl>
        <Url><![CDATA[%s]]></Url>
        </item>
        </Articles>
        </xml> 
        """



def check_event(msg_dict):
    '''if somebody subscribe this account, then return this message'''
    if msg_dict['Event'] == "subscribe" :   
        reply_text = u'''带Ta回家吧
                         输入r: 查看最新发布的宠物信息
                         '''
        echostr = textTpl % (FromUser, ToUser, int(time.time()),  
                    'text',reply_text)
        return echostr
    elif msg_dict['Event'] == "unsubscribe":
        reply_text = u'''感谢您的支持.'''
        echostr = textTpl % (
                FromUser, ToUser, int(time.time()),  
                    'text',reply_text)
        return echostr
    else:
        return None




def wechat_interact(msg_dict):
    msg_dict = ET.fromstring(msg_dict)
    MsgType = msg_dict.find('MsgType').text
    ToUser = msg_dict.find('ToUserName').text
    FromUser = msg_dict.find('FromUserName').text
    content = msg_dict.find('Content').text
    print MsgType, ToUser, FromUser 
    if MsgType == 'event': #return the welcome message
        return check_event(msg_dict)
    elif content == 'r': 
        print 1111
        kv = sae.kvdb.Client()
        pets_dict = kv.get_by_prefix('s', limit=2)
        if not pets_dict:
            reply_text = u'''Sorry, 数据库出现了一点小状况, 攻城狮正在修复ing...'''
        else:
            now = int(time.time())
            text_list = []
            text_list.append(FromUser)
            text_list.append(ToUser)
            text_list.append(now)
            for key, value in pets_dict:
                discription= """
                日期:%s
                年龄:%s
                性别:%s
                是否绝育:%s
                是否免疫:%s
                健康状况:%s
                联系方式:%s
                位置:%s
                备注:%s
                """ % (value['date'], value['age'], value['gender'], \
                	value['sterilization'], value['immunization'], \
                	value['health'], value['tel'],value['location'],\
                	value['supplement'])
                text_list.append(value['pet_title'])
                text_list.append(discription)
                text_list.append(value['photo_urls'][0])
                url = "http://taketahome.sinaapp.com/petpage/%s"% key
                text_list.append(url)
                print text_list
            return textTpl_image % tuple(text_list)
    elif content in ['h', 'H', 'help', 'Help']:
        reply_text = u'''r : 查看最近发布的宠物信息'''
    else:
        reply_text = u'''对不起, 目前功能尚不完善.'''
    
    echostr = textTpl % (
                FromUser, ToUser, int(time.time()),  
                    'text',reply_text)
    return echostr


            

