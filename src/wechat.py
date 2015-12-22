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
        echostr = textTpl % (
            msg_dict['FromUserName'], msg_dict['ToUserName'], int(time.time()),  
                    'text',reply_text)
        return echostr
    elif msg_dict['Event'] == "unsubscribe":
        reply_text = u'''感谢您的支持.'''
        echostr = textTpl % (
                msg_dict['FromUserName'], msg_dict['ToUserName'], int(time.time()),  
                    'text',reply_text)
        return echostr
    else:
        return None







def wechat_interact(msg_dict):
    msg_dict = ET.fromstring(msg_dict)
    MsgType = msg_dict.find('MsgType').text
    ToUser = msg_dict.find('ToUserName').text
    FromUser = msg_dict.find('FromUserName').text
    
    if msg_dict['MsgType'] == 'event': #return the welcome message
        return check_event(msg_dict)
    elif msg_dict['Content'] == 'r':  
        kv = sae.kvdb.Client()
        pets_dict = kv.get_by_perfix('s', limit=2)
        if not pets_dict:
            reply_text = u'''Sorry, 数据库出现了一点小状况, 攻城狮正在修复ing...'''
            echostr = textTpl % (
                msg_dict['FromUserName'], msg_dict['ToUserName'], int(time.time()),  
                    'text',reply_text)
            return echostr
        else:
        	pet_discription = []

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
                pets_discription.append(value['pet_title'])
                pets_discription.append(discription)
                pets_discription.append(value['photo_urls'][0])
                url = "http://taketahome.sinaapp.com/petpage/%s"% key
                pets_discription.append(url)

            








        if tag == "NULL":
            real_content = msg_dict['Content'][1:]
        else:
            real_content = msg_dict['Content'][1:(string_number-1)]
        msg_dict['Content'] = real_content
        msg_dict['Tag'] = tag
        item_number = save_message(msg_dict)
        reply_text = u'''Roger that. 这是第%s条日记.''' % item_number
        echostr = textTpl % (
                msg_dict['FromUserName'], msg_dict['ToUserName'], 
                int(time.time()), msg_dict['MsgType'],reply_text)
        return echostr
    elif msg_dict['Content'] == 'h':
        reply_text = u'''
        HELP:
        .+输入内容: write something
        r: read what you have written
        h: help
        d+数字:删除该条笔记
        c: clear all
        '''
        echostr = textTpl % (
                msg_dict['FromUserName'], msg_dict['ToUserName'],
                int(time.time()), msg_dict['MsgType'],reply_text)
        return echostr
    elif msg_dict['Content'] == 'r':  # read all messsage
        db_content = read_KVDB()
        all_content = '\n'.join(value['Content']+'#Tag:'+ 
                                value['Tag']+'#' for key, value in db_content)
        print all_content
        reply_text = u'''%s''' % all_content
        echostr = textTpl % (
                msg_dict['FromUserName'], msg_dict['ToUserName'], 
                int(time.time()), msg_dict['MsgType'],reply_text)
        return echostr
    elif msg_dict['Content'][0] == 'd': #delete one item
        delete_number = msg_dict['Content'][1:]
        search_key = 'No.'+delete_number
        return_text = u'''%s已经删除第%s条日记'''%(delete_item(search_key),
                                    delete_number)
        echostr = textTpl % (
                msg_dict['FromUserName'], msg_dict['ToUserName'], 
                int(time.time()), msg_dict['MsgType'],return_text)
        return echostr
    elif msg_dict['Content'] == "c":  # clear all
        result = delete_all()
        result_text = u'''%s已经删除全部内容'''% result
        echostr = textTpl % (
                msg_dict['FromUserName'], msg_dict['ToUserName'], 
                int(time.time()), msg_dict['MsgType'],result_text)
        return echostr
    else:
        reply_text = u'''
        .+输入内容: write something
        r: read what you have written
        h: help
        d+数字:删除该条笔记
        c: clear all
        '''
        echostr = textTpl % (
                msg_dict['FromUserName'], msg_dict['ToUserName'], 
                int(time.time()), msg_dict['MsgType'],reply_text)
        return echostr