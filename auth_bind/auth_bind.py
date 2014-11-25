#!/usr/bin/env python
#encoding=utf8
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
conn=MySQLdb.connect(host='192.168.1.210',user='moplus',passwd='Wd36sRpt182jENTTGxVf',db='uplusmain',port=3306,charset='utf8')
conn1=MySQLdb.connect(host='localhost',user='root',passwd='666666',db='uplus_auth',port=3306,charset='utf8')
cur1=conn1.cursor()
cur=conn.cursor()

def get_client_version(x):
        sql ='select client_version from uplusmain.user_statics where user_id=%d'%x
        print sql
        cur.execute(sql)
        client_version=cur.fetchall()
        print client_version
        return client_version[0][0]

def get_client_type(x):
        sql ='select client_type from uplusmain.user_info where user_id=%d'%i[0]
        cur.execute(sql)
        client_type=cur.fetchall()
        print client_type
        return client_type[0][0]
    
if __name__ == '__main__':
    ####插入第三方绑定内容
    count=cur.execute('SELECT user_id,site_name,auth_id,nick_name,access_token,access_token_secret,create_time,updte_time FROM uplusmain.oauth_bind limit 2' )
    print 'there has %s rows record' % count
    record_id=cur.fetchall()
    for i in record_id:
        #i[0]=user_id,i[1]=site_name,i[2]=auth_id,i[3]=nick_name,i[4]=access_token,i[5]=access_token_secret,i[6]=create_time,i[7]=update_time
        #获取client_version
        client_version=get_client_version(i[0])
        #获取client_type
        client_type=get_client_type(i[0])
        
        #分类表名和bind_type
        auth_table=''
        bind_type=0
        if i[1] == 'weibo':
            auth_table='sina_weibo_auth'
            bind_type=12
        elif i[1] == 'qqweibo':
            auth_table='tencent_weibo_auth'
            bind_type=13
        elif i[1] == 'qq':
            auth_table='qq_auth'
            bind_type=14
        elif i[1] == 'weixin':
            auth_table='weixin_auth'
            bind_type=15
        else:
            pass
        #插入*_auth表
        if i[3]!=None:
            nick_name=MySQLdb.escape_string(i[3])#MySQLdb.escape_string  can not处理null,need string
        else:
            nick_name=''
        sql='insert into uplus_auth.%s set username=\'%s\', nick_name=\'%s\',user_id=%d,access_token=\'%s\',create_time=\'%s\',update_time=\'%s\',version=0,security_token=\'%s\',phone_number=\'\''%(auth_table,i[2],nick_name,i[0],i[4],i[6],i[7],i[5])
        print sql
        cur1.execute(sql)
        #从*_auth表获取bind_id
        sql='select id from uplus_auth.%s where user_id=%d'%(auth_table,i[0])
        cur1.execute(sql)
        bind_id=cur1.fetchall()
        print bind_id[0][0]
    
        #插入user_bind记录
        sql='insert into uplus_auth.user_bind set user_id=%d, bind_type=%d,bind_id=%d,bind_status=0,create_time=\'%s\',update_time=\'%s\',version=0'%(i[0],bind_type,bind_id[0][0],i[6],i[7],)
        print sql
        cur1.execute(sql)
        #插入bind_history    
        sql='insert into uplus_auth_history.bind_history set bind_type=%d, need_bind_id=%d,user_id=%d,bind_status=0,client_type=%d,client_version=\'%s\',create_time=\'%s\''%(bind_type,bind_id[0][0],i[0],client_type,client_version,i[6])
        print sql
        cur1.execute(sql)    
        
    ####插入phone绑定内容
    count=cur.execute('select id,phone_number,create_time,update_time from uplusmain.user where length(phone_number)>7 limit 2')
    print 'there has %s rows record' % count
    record_id=cur.fetchall()
    for i in record_id:
        
        #i[0]=user_id,i[1]=phone_number,i[2]=create_time,i[3]=update_time,更新phonenumber_auth
        print i
        print i[1],i[2]
        print type(i[1]),type(i[2])
        
        #获取client_version
        client_version=get_client_version(i[0])
        #获取client_type
        client_type=get_client_type(i[0])
        
        #phone_number的bind_type为11
        bind_type=11
        #更新phonenumber_auth表
        sql='insert into uplus_auth.phonenumber_auth set phone_number=\'%s\', user_id=%s,password=\'\',create_time=\'%s\',update_time=\'%s\',version=0'%(i[1],i[0],i[2],i[3])
        print sql
        cur1.execute(sql)
        
      
        #从*_auth表获取bind_id
        sql='select id from uplus_auth.phonenumber_auth where user_id=%d'%i[0]
        cur1.execute(sql)
        bind_id=cur1.fetchall()
        print bind_id[0][0]
        
        #插入user_bind记录
        sql='insert into uplus_auth.user_bind set user_id=%d, bind_type=11,bind_id=%d,bind_status=0,phone_number=\'%s\',create_time=\'%s\',update_time=\'%s\',version=0'%(i[0],bind_id[0][0],i[1],i[2],i[3])
        print sql
        cur1.execute(sql)
        
        #i[0]=user_id,i[1]=phone_number,i[2]=create_time,i[3]=update_time,更新phonenumber_auth
        #插入bind_history
        sql='insert into uplus_auth_history.bind_history set bind_type=%d, need_bind_id=%d,user_id=%d,bind_status=0,client_type=%d,client_version=\'%s\',create_time=\'%s\''%(bind_type,bind_id[0][0],i[0],client_type,client_version,i[3])
        print sql
        cur1.execute(sql)
        
        #phonenumber插入其他auth表中
        auth=['uplus_auth.sina_weibo_auth','uplus_auth.tencent_weibo_auth','uplus_auth.qq_auth','uplus_auth.weixin_auth','uplus_auth.user_bind','uplus_auth_history.bind_history']
        for n in range(0, len(auth)):
            sql='update %s set phone_number=\'%s\' where user_id=%d'%(auth[n],i[1],i[0])
            print sql
            cur1.execute(sql)
    
    conn1.commit()
    cur1.close()
    conn1.close()
    conn.commit()
    cur.close()
    conn.close()
    print 'over'

