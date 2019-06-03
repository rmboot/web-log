from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView

import json
from .tasks import db
from datetime import datetime, timedelta

http_status_dict = {'1': ' 提示信息', '2': ' 成功', '3': ' 重定向', '4': ' 客户端错误', '5': ' 服务器端错误'}
province_data = [{'name': '江苏'}, {'name': '北京'}, {'name': '上海'}, {'name': '重庆'}, {'name': '河北'}, {'name': '河南'},
                 {'name': '云南'}, {'name': '辽宁'}, {'name': '黑龙江'}, {'name': '湖南'}, {'name': '安徽'}, {'name': '山东'},
                 {'name': '新疆'}, {'name': '江苏'}, {'name': '浙江'}, {'name': '江西'}, {'name': '湖北'}, {'name': '广西'},
                 {'name': '甘肃'}, {'name': '山西'}, {'name': '内蒙古'}, {'name': '陕西'}, {'name': '吉林'}, {'name': '福建'},
                 {'name': '贵州'}, {'name': '广东'}, {'name': '青海'}, {'name': '西藏'}, {'name': '四川'}, {'name': '宁夏'},
                 {'name': '海南'}, {'name': '台湾'}, {'name': '香港'}, {'name': '澳门'}]


@method_decorator(login_required, name='dispatch')
class IndexView(ListView):
    template_name = 'logtest/index.html'
    context_object_name = 'log'

    start = datetime.now()
    pre = start - timedelta(days=9)
    end = start + timedelta(days=1)
    start_day = str(start.year) + '-' + str(start.month) + '-' + str(start.day)
    pre_day = str(pre.year) + '-' + str(pre.month) + '-' + str(pre.day)
    end_day = str(end.year) + '-' + str(end.month) + '-' + str(end.day)

    def get_info(self, info):
        data = db.log.aggregate([
            {'$match': {'time_local': {'$gte': datetime.strptime(self.start_day, "%Y-%m-%d"),
                                       '$lt': datetime.strptime(self.end_day, "%Y-%m-%d")}}},
            {'$group': {'_id': '$' + info, 'count': {'$sum': 1}}},
            {'$project': {info: '$_id', 'count': '$count', '_id': 0}},
            {'$sort': {'count': -1}},
            {'$limit': 6}
        ])
        return data

    def get_queryset(self):
        date_10 = db.log.aggregate([
            {'$match': {'time_local': {'$gte': datetime.strptime(self.pre_day, "%Y-%m-%d"),
                                       '$lt': datetime.strptime(self.end_day, "%Y-%m-%d")}}},
            {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$time_local'}}, 'count': {'$sum': 1}}},
            {'$project': {'date': '$_id', 'count': '$count', '_id': 0}},
            {'$sort': {'date': 1}},
            # {'$limit': 10}
        ])
        date_data, count = [], []
        for i in date_10:
            date_data.append(i['date'])
            count.append(i['count'])
        url_data = self.get_info('url')
        remote_addr_data = self.get_info('remote_addr')
        return {'date_data': json.dumps(date_data), 'count': json.dumps(count),
                'url_data': url_data, 'remote_addr_data': remote_addr_data}


@method_decorator(login_required, name='dispatch')
class TodayAccessView(IndexView):
    template_name = 'logtest/today_access.html'
    context_object_name = 'today'

    def get_queryset(self):
        to_day = db.log.aggregate([
            {'$match': {'time_local': {'$gte': datetime.strptime(self.start_day, "%Y-%m-%d"),
                                       '$lt': datetime.strptime(self.end_day, "%Y-%m-%d")}}},
            {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d %H:%M', 'date': '$time_local'}},
                        'count': {'$sum': 1}}},
            {'$project': {'day': '$_id', 'count': '$count', '_id': 0}},
            {'$sort': {'day': 1}},
        ])
        data, count = [], []
        for i in to_day:
            data.append(i['day'].split(' ')[-1])
            count.append(i['count'])
        return {'data': json.dumps(data), 'count': json.dumps(count)}


@method_decorator(login_required, name='dispatch')
class RecentLogView(ListView):
    template_name = 'logtest/recent_log_table.html'
    context_object_name = 'recent_log'

    def get_queryset(self):
        data = db.log.find({}, {'_id': 0}).sort([('time_local', -1)]).limit(400)
        all_data = []
        for i in data:
            i['time_local'] = str(i['time_local'])
            all_data.append(i)
        return {'all_data': json.dumps(all_data)}


@method_decorator(login_required, name='dispatch')
class ErrLogView(ListView):
    template_name = 'logtest/err_log_table.html'
    context_object_name = 'err_log'

    def get_queryset(self):
        data = db.err_log.find({}, {'_id': 0}).sort([('time_local', -1)])
        all_data = []
        for i in data:
            i['time_local'] = str(i['time_local'])
            all_data.append(i)
        return {'all_data': json.dumps(all_data)}


@method_decorator(login_required, name='dispatch')
class HttpStatusPieView(ListView):
    template_name = 'logtest/http_status_pie.html'
    context_object_name = 'http_status_pie'

    def get_queryset(self):
        http_status = db.http_status.find({}, {'_id': 0})
        name, all = [], []
        for i in http_status:
            if i['name'][0] in http_status_dict:
                i['name'] = i['name'] + http_status_dict[i['name'][0]]
                name.append(i['name'])
                all.append(i)
        all_sort = sorted(all, key=lambda x: x['value'], reverse=True)
        return {'name': json.dumps(name), 'all': json.dumps(all_sort)}


@method_decorator(login_required, name='dispatch')
class HttpStatusLineView(HttpStatusPieView):
    template_name = 'logtest/http_status_line.html'
    context_object_name = 'http_status_line'


@method_decorator(login_required, name='dispatch')
class InnerIPView(ListView):
    template_name = 'logtest/inner_ip.html'
    context_object_name = 'inner'
    to_sum = '$count'

    def get_queryset(self):
        inner_ip = db.ip.aggregate([
            {'$match': {'$or': [{'country_id': 'CN'}, {'country_id': 'HK'}, {'country_id': 'TW'}]}},
            {'$group': {'_id': '$region', 'count': {'$sum': self.to_sum}}},
            {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
            {'$sort': {'value': -1}}
        ])
        data, count = [], 0
        for i in inner_ip:
            count += i['value']
            data.append(i)
        for a in province_data:
            a['value'] = 0
        for i in province_data:
            for j in data:
                if j['name'] == i['name']:
                    i['value'] = round(j['value'] / count * 100, 2)
        all_sort = sorted(province_data, key=lambda x: x['value'], reverse=True)
        return {'all': json.dumps(all_sort)}


@method_decorator(login_required, name='dispatch')
class InnerDiffIPView(InnerIPView):
    template_name = 'logtest/inner_diff_ip.html'
    context_object_name = 'inner_diff'
    to_sum = 1


@method_decorator(login_required, name='dispatch')
class OuterIPView(ListView):
    template_name = 'logtest/outer_ip.html'
    context_object_name = 'outer'
    to_sum = '$count'

    def get_queryset(self):
        outer_ip = db.ip.aggregate([
            {'$match': {
                '$and': [{'country_id': {'$ne': 'CN'}}, {'country_id': {'$ne': 'HK'}}, {'country_id': {'$ne': 'TW'}}]}},
            {'$group': {'_id': '$country', 'count': {'$sum': self.to_sum}}},
            {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
            {'$sort': {'value': -1}}
        ])
        data = [i for i in outer_ip]
        all, name = [], []
        for i in data:
            all.append(i)
            name.append(i['name'])
        return {'name': json.dumps(name), 'all': json.dumps(all)}


@method_decorator(login_required, name='dispatch')
class OuterDiffIPView(OuterIPView):
    template_name = 'logtest/outer_diff_ip.html'
    context_object_name = 'outer_diff'
    to_sum = 1


@method_decorator(login_required, name='dispatch')
class UABrowserBotView(ListView):
    template_name = 'logtest/ua_browser_bot.html'
    context_object_name = 'browser_bot'

    def get_queryset(self):
        data = db.user_agent.aggregate([
            {'$group': {'_id': '$' + self.context_object_name, 'count': {'$sum': '$count'}}},
            {'$project': {'name': '$_id', 'value': '$count', '_id': 0}},
            {'$sort': {'value': -1}}
        ])
        all, name = [], []
        for i in data:
            all.append(i)
            name.append(i['name'])
        return {'name': json.dumps(name), 'all': json.dumps(all)}


class UAOsView(UABrowserBotView):
    template_name = 'logtest/ua_os.html'
    context_object_name = 'os'


class UABrowserDetailView(UABrowserBotView):
    template_name = 'logtest/ua_browser_detail.html'
    context_object_name = 'browser'
