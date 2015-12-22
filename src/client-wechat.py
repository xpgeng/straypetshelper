#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mydaily-wechat-client
Author Shenlang

"""

import sys,requests
import time
import xml.etree.ElementTree as ET
reload(sys)
sys.setdefaultencoding('utf-8')

def main():
    print'''带Ta回家吧
    输入r: 查看最新发布的宠物信息
    '''
    while True:
        textTpl = """<xml>
                 <ToUserName><![CDATA[%s]]></ToUserName>
                 <FromUserName><![CDATA[%s]]></FromUserName> 
                 <CreateTime>%s</CreateTime>
                 <MsgType><![CDATA[text]]></MsgType>
                 <Content><![CDATA[%s]]></Content>
                 <MsgId>1234567890123456</MsgId>
                 </xml>"""
        send_content = raw_input('> ')
        echostr = textTpl % ('qqqq', 'wwww', int(time.time()), send_content)
        r = requests.post('http://localhost:8080/wechat', echostr)
        root = ET.fromstring(r.content)
        msg_dict = {}
        for child in root:
            msg_dict[child.tag] = child.text
        print msg_dict['Content']
if __name__ == '__main__':
    main()