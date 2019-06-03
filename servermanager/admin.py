from django.contrib import admin
from servermanager.models import BlockIPLog
import os


# Register your models here.
class EmailSendLogAdmin(admin.ModelAdmin):
    list_display = ('title', 'emailto', 'send_result', 'created_time')
    readonly_fields = ('title', 'emailto', 'send_result', 'created_time', 'content')

    def has_add_permission(self, request):
        return False


class BlockIPLogAdmin(admin.ModelAdmin):
    list_display = ('ip_addr', 'send_result', 'created_time')
    readonly_fields = ('ip_addr', 'send_result', 'created_time')
    actions = ['delete_model']

    def get_actions(self, request):
        actions = super(BlockIPLogAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_model(self, request, obj):
        for i in obj:
            os.system('sudo iptables -D INPUT -s %s -j DROP' % i.ip_addr)
            print('解禁:' + i.ip_addr)
            i.delete()
    delete_model.short_description = '解除禁止访问'

    def has_add_permission(self, request):
        return False
