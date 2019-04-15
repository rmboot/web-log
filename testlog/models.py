from mongoengine import *
import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.logtest


class Log(Document):
    remote_addr = StringField()
    time_local = DateTimeField()
    http_method = StringField()
    url = StringField()
    http_status = StringField()
    body_bytes_sent = StringField()
    http_referer = StringField()
    user_agent = StringField()


class Httpstatus(Document):
    name = StringField()
    value = IntField()


# http_status = Log.objects.exec_js(
#     "db.getCollection('log').aggregate([\
#     {'$group': {'_id': '$http_status', 'count': {'$sum': 1}}},\
#     {'$project':{'name':'$_id','value':'$count','_id':0}}])")
# http_status_list = []
# for i in http_status['_batch']:
#     http_status_list.append(i['name'])
# print(http_status)

# for i in x:
#     print(i['_id'],i['count'])
# x = Log.objects.exec_js("db.getCollection('httpstatus').find({},{'_id':0})")
# x = Log.objects.exec_js("db.getCollection('httpstatus').findOne()")
# print(x)

# for i in Httpstatus.objects({},{'_id':0}):
#     print(i.name)
# http_status_list = []
# for i in http_status:
#     http_status_list.append(i['name'])
# print(http_status)

# pipeline = [
#  {'$group': {'_id': "$fName", 'count': {'$sum': 1}}},
#  ]
# for i in G_mongo['test'].aggregate(pipeline):
#  print i
# print(Log.objects.exec_js("find({'http_status':'0'})"))
# user_search = Users.objects(age__gte=10, age__lt=33).order_by('name')
# log = Log.objects(time_local__lte=datetime(2019, 3, 10, 0, 0))
# print(log[0].remote_addr)
# x = datetime(2018, 9, 10, 0, 0)
# x = datetime.now()
# x = ISODate("2016-01-01T00:00:00Z")
# log = Log.objects(time_local__gte=datetime(2019, 3, 6, 10), time_local__lte=datetime(2019, 3, 6, 22))
# for i in log:
#     print("remote_addr:", i.remote_addr, "url:", i.url, "time_local:", i.time_local)

# class Users(Document):
#     username = StringField(required=True)
#     password = StringField(required=True)
#
#
# user = Users(username='jack', password='admin')
# user.save()
# print(user.username)
# user.save()

# users = Users.objects.all()
# for u in users:
#     print("name:", u.username, ",password:", u.password)
