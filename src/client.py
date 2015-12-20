#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Project: SPH
Author: Shenlang



注意: 使用时记得修改链接. ;-)



"""

import sys,requests
import time
reload(sys)
sys.setdefaultencoding('utf-8')

def main():
    print'''Hello. 
         你要干啥???
         d.key: 删除该key对应的数据
         dp.key_prefix: 删除此前缀的所有数据  
         backup: 数据库备份
         get.prefix: 查看该前缀的所有数据
         ca: 清空数据库. 慎用!!
         '''
    while True:  
        data = raw_input('> ')
        r = requests.post('http://localhost:8080/client', data={'data':data})   
        print r.content
if __name__ == '__main__':
    main()