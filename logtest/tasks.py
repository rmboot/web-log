import pymongo
import os
import re
import json
import time
import random
from urllib import request
from datetime import datetime
from user_agents import parse
from servermanager.models import BlockIPLog
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

from logtest.utils import send_comment_email
from weblog.utils import block_ip

client = pymongo.MongoClient("mongodb://root:12345678@localhost:27017/")
db = client.nginx_log_ok
pattern = re.compile(
    r"""(?P<remote_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<time_local>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(?P<http_method>GET|POST|PATCH|PUT|DELETE|OPTIONS|HEAD) )(?P<url>.+)( http\/1\.1")) (?P<http_status>\d{3}) (?P<body_bytes_sent>\d+) (["](?P<http_referer>(\-)|(.+))["]) (["](?P<user_agent>.+)["])""",
    re.IGNORECASE)

# path = '/home/zhangwang/Desktop/log/access.log.test'

# path = '/home/zhangwang/Desktop/access/access.log.17'

path = '/var/log/nginx/access.log'


def now_lines(path):
    if os.path.exists(path):
        with open(path, 'r') as fr:
            return len(fr.readlines())


def log_to_ip():
    ip = db.log.aggregate([
        {'$group': {'_id': '$remote_addr', 'count': {'$sum': 1}}},
        {'$project': {'remote_addr': '$_id', 'count': '$count', '_id': 0}},
    ])

    while ip.alive:
        i = ip.next()
        match_count = db.ip.count_documents({'remote_addr': i['remote_addr']})  # 原集合没有匹配=0 需要插入
        need_update = db.ip.count_documents({'remote_addr': i['remote_addr'], 'count': {'$ne': i['count']}})
        # 原集合有匹配且值变化=1 需要更新
        if match_count == 0:
            db.ip.insert_one({'remote_addr': i['remote_addr'], 'count': i['count'], 'isp': ''})
            print('insert_ip')
            continue  # 插入操作多 插入放前面
        if need_update == 1:
            db.ip.update_one({'remote_addr': i['remote_addr']}, {'$set': {'count': i['count']}})
            print('update_ip')


def log_to_http_status():
    http_status = db.log.aggregate([
        {'$group': {'_id': '$http_status', 'count': {'$sum': 1}}},
        {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
    ])
    while http_status.alive:
        i = http_status.next()
        match_count = db.http_status.count_documents({'name': i['name']})  # 原集合没有匹配=0 需要插入
        need_update = db.http_status.count_documents({'name': i['name'], 'value': {'$ne': i['value']}})
        # 原集合有匹配且值变化=1 需要更新
        if need_update == 1:
            db.http_status.update_one({'name': i['name']}, {'$set': {'value': i['value']}})
            print('update_http_status')
            continue  # 更新操作多 更新放前面
        if match_count == 0:
            db.http_status.insert_one({'name': i['name'], 'value': i['value']})
            print('insert_http_status')


def log_to_user_agent():
    user_agent = db.log.aggregate([
        {'$group': {'_id': '$user_agent', 'count': {'$sum': 1}}},
        {'$project': {'user_agent': '$_id', 'count': '$count', '_id': 0}},
    ])
    while user_agent.alive:
        i = user_agent.next()
        match_count = db.user_agent.count_documents({'user_agent': i['user_agent']})  # 原集合没有匹配=0 需要插入
        need_update = db.user_agent.count_documents({'user_agent': i['user_agent'], 'count': {'$ne': i['count']}})
        # 原集合有匹配且值变化=1 需要更新
        if match_count == 0:
            db.user_agent.insert_one({'user_agent': i['user_agent'], 'count': i['count'], 'browser_bot': ''})
            print('insert_user_agent')
            continue  # 插入操作多 插入放前面
        if need_update == 1:
            db.user_agent.update_one({'user_agent': i['user_agent']}, {'$set': {'count': i['count']}})
            print('update_user_agent')


def user_agent_to_detail():
    no_detail_ua_count = db.user_agent.count_documents({'browser_bot': ''})
    if no_detail_ua_count != 0:
        no_detail_ua = db.user_agent.find({'browser_bot': ''})
        for i in no_detail_ua:
            ua = parse(i['user_agent'])
            if ua.is_bot:
                browser_bot = 'Bot'
            else:
                browser_bot = ua.browser.family
            db.user_agent.update_one({'user_agent': i['user_agent']},
                                     {'$set': {'browser_bot': browser_bot,
                                               'browser': ua.browser.family + ' ' + ua.browser.version_string,
                                               'os': ua.os.family + ' ' + ua.os.version_string}
                                      })
    else:
        print('user_agent_detail_ok')


def ip_to_detail():
    def ip_to_db(ip):
        url = 'http://ip.taobao.com/service/getIpInfo.php?ip=' + ip
        headers = [{'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
                   {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1'},
                   {
                       'User-Agent': ' Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1'},
                   {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                   AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'},
                   {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) \
                   AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}]
        rand_index = random.randint(0, len(headers) - 1)
        req = request.Request(url=url, headers=headers[rand_index])
        data = request.urlopen(req).read().decode('utf-8')
        json_data = json.loads(data)
        if json_data['code'] == 0:
            return json_data['data']

    no_detail_ip_count = db.ip.count_documents({'isp': ''})

    if no_detail_ip_count != 0:
        count = 1
        no_detail_ip = db.ip.find({'isp': ''})
        for i in no_detail_ip:
            time.sleep(random.randint(3, 4))
            data = ip_to_db(i['remote_addr'])
            for k in list(data.keys()):
                if k != 'country' and k != 'region' and k != 'city' and k != 'country_id' \
                        and k != 'isp' and k != 'ip':
                    data.pop(k)
            db.ip.update_one({'remote_addr': data['ip']}, {'$set': data})
            print(count, data['country'])
            count += 1
    else:
        print('ip_detail_ok')


log_old = now_lines(path)
# log_old = 0

# user_agent_to_detail()
# ip_to_detail()

"""
def log_to_mongodb():
    global log_old
    print('log_old：', log_old)
    log_new = now_lines(path)
    print('log_new：', log_new)
    if log_new > log_old:
        with open(path, 'r') as f:
            lines = f.readlines()[-(log_new - log_old):]
            pre_log = {"remote_addr": "", "time_local": "", "http_status": ''}
            err_status = {'404', '301'}
            count = 0
            for line in lines:
                log, err_log = {}, {}
                m = pattern.match(line)
                if m is None:
                    s = line.split(' ')
                    err_log['remote_addr'] = s[0]
                    time_local = s[3][1:].replace(":", " ", 1)
                    err_log["time_local"] = datetime.strptime(time_local, "%d/%b/%Y %H:%M:%S")
                    err_log["all"] = line
                    db.err_log.insert_one(err_log)
                    if BlockIPLog.objects.filter(ip_addr=err_log['remote_addr']):
                        print('无法匹配该日志记录 IP:' + err_log['remote_addr'] + ' 已经禁止')
                    else:
                        # send_comment_email('无法匹配该日志记录',
                        #                    '攻击来源IP:'+err_log['remote_addr'],
                        #                    '详细日志记录:'+line)
                        # block_ip(err_log['remote_addr'])
                        print(err_log)
                    continue
                elif pre_log["http_status"] == m.group('http_status') \
                        and pre_log["remote_addr"] == m.group('remote_addr') \
                        and pre_log["time_local"] == m.group('time_local') \
                        and m.group('http_status') in err_status:
                    if BlockIPLog.objects.filter(ip_addr=m.group('remote_addr')):
                        print(m.group('http_status') + '访问频繁 IP:' + m.group('remote_addr') + ' 已经禁止')
                    else:
                        # send_comment_email(m.group('http_status')+'访问频繁',
                        #                    '攻击来源IP:'+m.group('remote_addr'),
                        #                    '详细日志记录:'+line)
                        # block_ip(m.group('remote_addr'))
                        print('访问频繁 IP:' + m.group('remote_addr'))
                    continue
                else:
                    dt = m.group('time_local').split(' ')
                    log["remote_addr"] = m.group('remote_addr')
                    log["time_local"] = datetime.strptime(dt[0], "%d/%b/%Y:%H:%M:%S")
                    log["http_method"] = m.group('http_method')
                    log["url"] = m.group('url')
                    log["http_status"] = m.group('http_status')
                    log["body_bytes_sent"] = m.group('body_bytes_sent')
                    log["http_referer"] = m.group('http_referer')
                    log["user_agent"] = m.group('user_agent')
                    db.log.insert_one(log)
                    count += 1
                    # print(log)
                    pre_log["remote_addr"] = m.group('remote_addr')
                    pre_log["time_local"] = m.group('time_local')
                    pre_log["http_status"] = m.group('http_status')
                    # print(pre_log)
            print('log_add', count)
    log_old = log_new
    # log_to_ip()
    # log_to_http_status()
    # log_to_user_agent()
    # user_agent_to_detail()
for i in range(8,17,1):
    path = '/home/zhangwang/Desktop/access/access.log.'+str(i)
    log_old = 0
    log_to_mongodb()
"""

try:
    # 实例化调度器
    scheduler = BackgroundScheduler()
    # 调度器使用DjangoJobStore()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    @register_job(scheduler, 'interval', seconds=5)
    def log_to_mongodb():
        global log_old
        print('log_old：', log_old)
        log_new = now_lines(path)
        print('log_new：', log_new)
        if log_new > log_old:
            with open(path, 'r') as f:
                lines = f.readlines()[-(log_new - log_old):]
                pre_log = {"remote_addr": "", "time_local": "", "http_status": ''}
                err_status = {'404', '301'}
                count = 0
                for line in lines:
                    log, err_log = {}, {}
                    m = pattern.match(line)
                    if m is None:
                        s = line.split(' ')
                        err_log['remote_addr'] = s[0]
                        time_local = s[3][1:].replace(":", " ", 1)
                        err_log["time_local"] = datetime.strptime(time_local, "%d/%b/%Y %H:%M:%S")
                        err_log["all"] = line
                        db.err_log.insert_one(err_log)
                        if BlockIPLog.objects.filter(ip_addr=err_log['remote_addr']):
                            print('无法匹配该日志记录 IP:' + err_log['remote_addr'] + ' 已经禁止')
                        else:
                            send_comment_email('无法匹配该日志记录',
                                               '攻击来源IP:'+err_log['remote_addr'],
                                               '详细日志记录:'+line)
                            block_ip(err_log['remote_addr'])
                            pass
                            print(err_log)
                        continue
                    elif pre_log["http_status"] == m.group('http_status') \
                            and pre_log["remote_addr"] == m.group('remote_addr') \
                            and pre_log["time_local"] == m.group('time_local') \
                            and m.group('http_status') in err_status:
                        if BlockIPLog.objects.filter(ip_addr=m.group('remote_addr')):
                            print(m.group('http_status')+'访问频繁 IP:' + m.group('remote_addr') + ' 已经禁止')
                        else:
                            send_comment_email(m.group('http_status')+'访问频繁 IP:'+m.group('remote_addr'),
                                               '攻击来源IP:'+m.group('remote_addr'),
                                               '详细日志记录:'+line)
                            block_ip(m.group('remote_addr'))
                            pass
                        continue
                    else:
                        dt = m.group('time_local').split(' ')
                        log["remote_addr"] = m.group('remote_addr')
                        log["time_local"] = datetime.strptime(dt[0], "%d/%b/%Y:%H:%M:%S")
                        log["http_method"] = m.group('http_method')
                        log["url"] = m.group('url')
                        log["http_status"] = m.group('http_status')
                        log["body_bytes_sent"] = m.group('body_bytes_sent')
                        log["http_referer"] = m.group('http_referer')
                        log["user_agent"] = m.group('user_agent')
                        db.log.insert_one(log)
                        count += 1
                        # print(log)
                        pre_log["remote_addr"] = m.group('remote_addr')
                        pre_log["time_local"] = m.group('time_local')
                        pre_log["http_status"] = m.group('http_status')
                        # print(pre_log)
                print('log_add', count)
            log_to_ip()
            log_to_http_status()
            log_to_user_agent()
            user_agent_to_detail()
        log_old = log_new


    @register_job(scheduler, 'interval', minutes=5)
    def ip_to_detail():
        def ip_to_db(ip):
            url = 'http://ip.taobao.com/service/getIpInfo.php?ip=' + ip
            headers = [{'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
                       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1'},
                       {
                           'User-Agent': ' Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1'},
                       {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                       AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'},
                       {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) \
                       AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}]
            rand_index = random.randint(0, len(headers) - 1)
            req = request.Request(url=url, headers=headers[rand_index])
            data = request.urlopen(req).read().decode('utf-8')
            json_data = json.loads(data)
            if json_data['code'] == 0:
                return json_data['data']

        no_detail_ip_count = db.ip.count_documents({'isp': ''})

        if no_detail_ip_count != 0:
            count = 1
            no_detail_ip = db.ip.find({'isp': ''})
            for i in no_detail_ip:
                time.sleep(random.randint(3, 4))
                data = ip_to_db(i['remote_addr'])
                for k in list(data.keys()):
                    if k != 'country' and k != 'region' and k != 'city' and k != 'country_id' \
                            and k != 'isp' and k != 'ip':
                        data.pop(k)
                db.ip.update_one({'remote_addr': data['ip']}, {'$set': data})
                print(count, data['country'])
                count += 1
        else:
            print('ip_detail_ok')

    # 监控任务
    register_events(scheduler)
    # 调度器开始
    scheduler.start()
except Exception as e:
    print(e)
    # 报错则调度器停止执行
    scheduler.shutdown()
