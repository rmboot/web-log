from django.contrib.admin import AdminSite
# 模型
from django.contrib.admin.models import LogEntry
from django.contrib.sites.models import Site
from servermanager.models import EmailSendLog, BlockIPLog
from account.models import WebLogUser
from logtest.models import DjangoJob, DjangoJobExecution
# 模型管理
from weblog.log_entry_admin import LogEntryAdmin
from django.contrib.sites.admin import SiteAdmin
from account.admin import WebLogUserAdmin
from logtest.admin import DjangoJobAdmin, DjangoJobExecutionAdmin
from servermanager.admin import EmailSendLogAdmin, BlockIPLogAdmin


class WebLogAdminSite(AdminSite):
    site_header = '日志分析可视化系统'
    site_title = '管理后台'

    def __init__(self, name='admin'):
        super().__init__(name)

    def has_permission(self, request):
        return request.user.is_superuser


admin_site = WebLogAdminSite(name='admin')
admin_site.register(Site, SiteAdmin)  # 站点名称管理
admin_site.register(WebLogUser, WebLogUserAdmin) # 站点用户管理
admin_site.register(DjangoJob, DjangoJobAdmin)  # 日志处理任务管理
admin_site.register(DjangoJobExecution, DjangoJobExecutionAdmin)  # 日志处理任务调度管理
admin_site.register(EmailSendLog, EmailSendLogAdmin)  # 预警邮件日志管理
admin_site.register(BlockIPLog, BlockIPLogAdmin)  # 禁止IP日志管理
admin_site.register(LogEntry, LogEntryAdmin)  # 站点日志管理
