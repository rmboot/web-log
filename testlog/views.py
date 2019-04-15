from django.views.generic import View, ListView
from django.shortcuts import render
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

import json
from .models import Log, db


class IndexView(View):
    def pagination(self, request, data, one_page=1000):
        try:
            page = request.GET.get('page', 1)
        except(PageNotAnInteger, EmptyPage):
            page = 1
        p = Paginator(data, one_page, request=request)
        return p.page(page)

    def get(self, request):
        url = request.GET.get('url')
        if url:
            data = Log.objects(url=url)
        else:
            data = Log.objects()
        p_data = IndexView.pagination(self=self, request=request, data=data)
        return render(request, 'testlog/index.html', {'data': p_data})


class HttpStatusView(View):
    def get(self, request):
        http_status_dict = {'1': ' 提示信息', '2': ' 成功', '3': ' 重定向', '4': ' 客户端错误', '5': ' 服务器端错误', 'e': ' 不符合解析规则', }
        http_status = db.http_status.find({}, {'_id': 0})
        http_status_all, http_status_name = [], []
        for i in http_status:
            if i['name'][0] in http_status_dict:
                i['name'] = i['name'] + http_status_dict[i['name'][0]]
                http_status_all.append(i)
                http_status_name.append(i['name'])
        return render(request, 'testlog/http_status.html',
                      {'http_status_name': json.dumps(http_status_name),
                       'http_status_all': json.dumps(http_status_all)})


class HttpStatusLineView(View):
    def get(self, request):
        http_status_dict = {'1': ' 提示信息', '2': ' 成功', '3': ' 重定向', '4': ' 客户端错误', '5': ' 服务器端错误', 'e': ' 不符合解析规则', }
        http_status = db.http_status.find({}, {'_id': 0})
        http_status_all, http_status_name = [], []
        for i in http_status:
            if i['name'][0] in http_status_dict:
                i['name'] = i['name'] + http_status_dict[i['name'][0]]
                http_status_all.append(i)
                http_status_name.append(i['name'])
        return render(request, 'testlog/http_status_line.html',
                      {'http_status_name': json.dumps(http_status_name),
                       'http_status_all': json.dumps(http_status_all)})


class InnerIPView(View):
    def get(self, request):
        inner_ip = db.ip.aggregate([
            {'$match': {'$or': [{'country_id': 'CN'}, {'country_id': 'HK'}, {'country_id': 'TW'}]}},
            {'$group': {'_id': '$region', 'count': {'$sum': 1}}},
            {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
            {'$sort': {'value': -1}}
        ])
        data, count = [], 0
        for i in inner_ip:
            count += i['value']
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
                    i['value'] = round(j['value'] / count * 100, 2)
        all_data_sort = sorted(all_data, key=lambda x: x['value'], reverse=True)
        return render(request, 'testlog/inner_ip.html', {'ip_all': json.dumps(all_data_sort)})


class InnerIPIPView(View):
    def get(self, request):
        inner_ip = db.ip.aggregate([
            {'$match': {'$or': [{'country_id': 'CN'}, {'country_id': 'HK'}, {'country_id': 'TW'}]}},
            {'$group': {'_id': '$region', 'count': {'$sum': '$value'}}},
            {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
            {'$sort': {'value': -1}}
        ])
        data, count = [], 0
        for i in inner_ip:
            count += i['value']
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
                    i['value'] = round(j['value'] / count * 100, 2)
        all_data_sort = sorted(all_data, key=lambda x: x['value'], reverse=True)
        return render(request, 'testlog/inner_ip_ip.html', {'ip_all': json.dumps(all_data_sort)})


class OuterIPView(View):
    def get(self, request):
        outer_ip = db.ip.aggregate([
            {'$match': {'$and': [{'country_id': {'$ne': 'CN'}}, {'country_id': {'$ne': 'HK'}}, {'country_id': {'$ne': 'TW'}}]}},
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
            {'$sort': {'value': -1}}
        ])
        data = []
        for i in outer_ip:
            data.append(i)
        outer_ip_all, outer_ip_name = [], []
        for i in data:
            outer_ip_all.append(i)
            outer_ip_name.append(i['name'])
        return render(request, 'testlog/outer_ip.html',
                      {'outer_ip_name': json.dumps(outer_ip_name),
                       'outer_ip_all': json.dumps(outer_ip_all)})


class OuterIPIPView(View):
    def get(self, request):
        outer_ip = db.ip.aggregate([
            {'$match': {'$and': [{'country_id': {'$ne': 'CN'}}, {'country_id': {'$ne': 'HK'}}, {'country_id': {'$ne': 'TW'}}]}},
            {'$group': {'_id': '$country', 'count': {'$sum': '$value'}}},
            {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
            {'$sort': {'value': -1}}
        ])
        data = []
        for i in outer_ip:
            data.append(i)
        outer_ip_all, outer_ip_name = [], []
        for i in data:
            outer_ip_all.append(i)
            outer_ip_name.append(i['name'])
        return render(request, 'testlog/outer_ip_ip.html',
                      {'outer_ip_name': json.dumps(outer_ip_name),
                       'outer_ip_all': json.dumps(outer_ip_all)})


class UserAgentBrowserView(ListView):
    template_name = 'testlog/user_agent_browser.html'
    context_object_name = 'user_agent'

    def get_queryset(self):
        browser = db.user_agent.aggregate([
            {'$group': {'_id': '$browser', 'count': {'$sum': '$value'}}},
            {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
            {'$sort': {'value': -1}}
        ])
        browser_all, browser_name = [], []
        for i in browser:
            browser_all.append(i)
            browser_name.append(i['name'])
        return {'browser_name': json.dumps(browser_name), 'browser_all': json.dumps(browser_all)}


# class UserAgentOsView(View):
#     def get(self, request):
#         os = db.user_agent.aggregate([
#             {'$group': {'_id': '$os', 'count': {'$sum': '$value'}}},
#             {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
#             {'$sort': {'value': -1}}
#         ])
#         os_all, os_name = [], []
#         for i in os:
#             os_all.append(i)
#             user_agent_name.append(i['name'])
#         return render(request, 'testlog/user_agent_browser.html',
#                       {'user_agent_name': json.dumps(user_agent_name),
#                        'user_agent_all': json.dumps(user_agent_all)})