#-*- coding:utf-8 -*-
import psutil
import datetime
import time
from psutil import cpu_percent
from flask import Flask,render_template,request,jsonify
import pymysql
from post_mail import post_mail1
db = pymysql.connect('localhost','root','123456','test')
cursor = db.cursor()
# sql_s = """select job_name,job_desc,comp_name,work_addr,education,work_years,min_salary,max_salary,comp_url,job_detail_url from lagou1 ORDER BY RAND() limit 15"""
app = Flask(__name__)

info_dic = {}
isok = True
#-----------------cpu----------------
def cpu_info():
    #cpu个数
    global info_dic
    cpu_num = psutil.cpu_count(logical=False)
    #CPU的使用率
    cpu_percent = (str(psutil.cpu_percent(1))) 
#     print(u"cup使用率: %s" % cpu_percent+ '%')
    info_dic = dict(cpu_num=cpu_num,cpu_percent=cpu_percent)
    return info_dic

#-------------------内存-----------------
def memory_info():
#     global info_dic
    mem_total = str(round(psutil.virtual_memory().total / (1024.0 * 1024.0 * 1024.0), 2))
    mem_free = str(round(psutil.virtual_memory().free / (1024.0 * 1024.0 * 1024.0), 2))
    mem_used = str(round((psutil.virtual_memory().total - psutil.virtual_memory().free)/(1024.0 * 1024.0 * 1024.0),2))
    # mem_percent = float((psutil.virtual_memory().total - psutil.virtual_memory().free)) / float(psutil.virtual_memory().total)
    mem_percent = psutil.virtual_memory().percent
#     print('内存总空间:%s' % mem_total+'G')
#     print('内存可用空间:%s'%mem_free+'G')
#     print('内存已用空间:%s'%mem_used+'G')
#     print('内存使用率:%s'%mem_percent+'%')
    info_dic.update(mem_total=mem_total,mem_free=mem_free,mem_used=mem_used,mem_percent=mem_percent)
    return info_dic



# -----------------系统用户------------------
def user_info():
#     global info_dic
    users_count = len(psutil.users())
    users_list = ",".join([u.name for u in psutil.users()])
#     print(u"当前有%s个用户，分别是 %s" % (users_count, users_list))
    info_dic.update(users_count=users_count,users_list=users_list)
    return info_dic

def net_info():  
    # -------------------网卡---------------------
#     global info_dic
    net = psutil.net_io_counters()
    sent = round((net.bytes_sent / 1024 / 1024),2)
    recvs = round((net.bytes_recv / 1024 / 1024),2)
#     print('网卡发送 : %sM' % sent)
#     print('网卡接收:%sM' % recvs)
    info_dic.update(sent=sent,recvs=recvs)
    return info_dic


def disk_info():
    # --------------硬盘信息------------------
    # -----------硬盘信息，单位G-----------
    disk_list = []
    diskinfo = psutil.disk_partitions()
    for i in diskinfo:
        disk_info = []
        try:
            info = psutil.disk_usage(i.device)
            disk_name = i.device
#             print(disk_name)
            disk_total = int(info.total / (1024 * 1024 * 1024))
            disk_used = int(info.used/(1024 * 1024 * 1024))
            disk_free = disk_total - disk_used
#             print('总大小:' + str(disk_total)+'G')
#             print('已用:' + str(disk_used)+'G')
#             print('可用:' + str(disk_free)+'G')
    
            disk_list.append([disk_name,disk_total,disk_used,disk_free])
        except:
            continue
    info_dic.update(disk_list=disk_list)
    return info_dic

# print(info_dic)
def process_info():
    pros_list = []
    #--------------进程信息------------------
    for pnum in psutil.pids():
        try:
            p = psutil.Process(pnum)
            pname = p.name()
            pmem_percent = round(p.memory_percent(),2)
            pstatus = p.status()
            pcreat_time = p.create_time()
            if pmem_percent > 1:
    #             print(u"进程名 %-20s  内存利用率 %-18s 进程状态 %-10s 创建时间 %-10s " \
    #                 % (pname, pmem_percent, pstatus, pcreat_time)) 
                pros_list.append([pname, pmem_percent, pstatus, pcreat_time])
        except:
            pass
    info_dic.update(pros_list=pros_list)
    return info_dic
memory_info()
user_info()
net_info()
disk_info() 
process_info()

# @app.route('/')
# def first():
#     return render_template('index.html',dic=info_dic)
#注册
@app.route('/register',methods=['GET'])
def register():
    return render_template('register.html')

#注册的提交
@app.route('/register',methods=['POST'])
def register_post():
    name = request.form['username']
    pwd1 = request.form['password']
    pwd2 = request.form['confirm_password']
    mail = request.form['email']
    sql = """select * from userpwd where username = '%s'
    """%(name)
    if cursor.execute(sql):
        return render_template('register.html',message='用户名已存在')
    elif pwd1 != pwd2:
        return render_template('register.html',message='前后密码不一致，请输入')
    sql_insert = """insert into userpwd(username,email,passwd) values('%s','%s','%s')
         """%(name,mail,pwd1)
    cursor.execute(sql_insert)
    db.commit()
    return render_template('login.html',message='注册成功，可以登陆了') 

@app.route('/login',methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/index',methods=['POST'])
def login_post():
    name = request.form['username']
    passwd =  request.form['password']
    
    sql = """select * from userpwd where username='%s'
    """%(name)
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        if res[-1] == passwd:
            return render_template('index.html',dic=info_dic,username=psutil.users()[0].name)   
    return render_template('login.html',message='用户名或密码错误，请重新输入')

@app.route('/addnumber')
def data1():
    time1 = time.time()
    sql_insert = """insert into cpuinfo(time1,cpu_percent) values(%s,%s)"""%(time1,psutil.cpu_percent(1))
    cursor.execute(sql_insert)
    db.commit()
    time.sleep(1)
    sql = """select cpu_percent from cpuinfo where time1=%s"""%time1
    cursor.execute(sql)
    results = cursor.fetchone()
    global isok
    if isok == True and psutil.cpu_percent(1) > 30.0:  #为了只提示一次
        post_mail1.post1()  #发送邮件的代码
        isok = False
    dics = {'dat':float(results[0])}
    return jsonify(dics)
if __name__ == '__main__':
    app.run(debug=True)