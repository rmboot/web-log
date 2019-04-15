import json
import time
import random
import pymongo
from urllib import request
from user_agents import parse

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.logtest

# ip to detail
"""
def ip_to_db(ip):
    url = 'http://ip.taobao.com/service/getIpInfo.php?ip=' + ip
    headers = [{'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
               {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1'},
               {'User-Agent': ' Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1'},
               {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'},
               {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) \
               AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}]
    rand_index = random.randint(0, len(headers) - 1)
    req = request.Request(url=url, headers=headers[rand_index])
    data = request.urlopen(req).read().decode('utf-8')
    jsondata = json.loads(data)
    if jsondata['code'] == 0:
        return jsondata['data']


count = 1
ip = db.ip_copy.find({}, {'_id': 0})
for i in ip:
    if i['isp'] == '':
        time.sleep(random.randint(3, 4))
        data = ip_to_db(i['name'])
        for k in list(data.keys()):
            if k != 'country' and k != 'region' and k != 'city' and k != 'country_id' and k != 'isp' and k != 'ip':
                data.pop(k)
        db.ip_copy.update_one({'name': data['ip']}, {'$set': data})
        print(count, data['country'])
        count += 1
"""
# httpstatus to pie show
"""
http_status = db.httpstatus.find({}, {'_id': 0})
http_status_all, http_status_name = [], []
http_status_dict = {'1': ' 提示信息 - 表示请求已被成功接收，继续处理',
                    '2': ' 成功 - 表示请求已被成功接收，理解，接受',
                    '3': ' 重定向 - 要完成请求必须进行更进一步的处理',
                    '4': ' 客户端错误 - 请求有语法错误或请求无法实现',
                    '5': ' 服务器端错误 - 服务器未能实现合法的请求',
                    'e': ' 自定义危险请求 - 不符合解析规则', }
for i in http_status:
    if i['name'][0] in http_status_dict:
        i['name'] = i['name']+http_status_dict[i['name'][0]]
        http_status_all.append(i)
        http_status_name.append(i['name'])
print(http_status_all)
print(http_status_name)
"""
# internal ip
"""
ip = db.ip.aggregate([
        {'$match': {'country_id': 'CN'}},
        {'$group': {'_id': '$region', 'count': {'$sum': 1}}},
        {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
        {'$sort': {'value': -1}}
    ])
data = []
for i in ip:
    data.append(i)
all_data = [{'name': '江苏'}, {'name': '北京'}, {'name': '上海'}, {'name': '重庆'}, {'name': '河北'}, {'name': '河南'},
            {'name': '云南'}, {'name': '辽宁'}, {'name': '黑龙江'}, {'name': '湖南'}, {'name': '安徽'}, {'name': '山东'},
            {'name': '新疆'}, {'name': '江苏'}, {'name': '浙江'}, {'name': '江西'}, {'name': '湖北'}, {'name': '广西'},
            {'name': '甘肃'}, {'name': '山西'}, {'name': '内蒙古'}, {'name': '陕西'}, {'name': '吉林'}, {'name': '福建'},
            {'name': '贵州'}, {'name': '广东'}, {'name': '青海'}, {'name': '西藏'}, {'name': '四川'}, {'name': '宁夏'},
            {'name': '海南'}, {'name': '台湾'}, {'name': '香港'}, {'name': '澳门'}]
for a in all_data:
    a['value'] = 0
for i in all_data:
    for j in data:
        if j['name'] == i['name']:
            i['value'] = j['value']
all_data_sort = sorted(all_data, key=lambda x: x['value'], reverse=True)
print(all_data_sort)
"""
# useragent to mongodb
"""
agent = db.log.aggregate([
    {'$group': {'_id': '$user_agent', 'count': {'$sum': 1}}},
    {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
    {'$sort': {'value': -1}}
])
num = 0
for i in agent:
    num += 1
    user_agent = parse(i['name'])
    db.user_agent.insert_one({'name': i['name'], 'value': i['value'],
                              'browser': user_agent.browser.family,
                              'browser_version': user_agent.browser.version_string,
                              'os': user_agent.os.family,
                              'os_version': user_agent.os.version_string})
print(num)
"""

