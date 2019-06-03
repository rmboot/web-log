from django.db import models

# Create your models here.
class EmailSendLog(models.Model):
    emailto = models.CharField('收件人', max_length=300)
    title = models.CharField('邮件标题', max_length=2000)
    content = models.TextField('邮件内容')
    send_result = models.BooleanField('结果', default=False)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '预警邮件日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']


class BlockIPLog(models.Model):
    ip_addr = models.CharField('IP', max_length=20,unique=True)
    send_result = models.BooleanField('结果', default=False)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.ip_addr

    # def delete(self):
    #     os.system('sudo iptables -D INPUT -s %s -j DROP' % self.ip_addr)
    #     print(self.ip_addr)
    #     super(BlockIPLog, self).delete()

    class Meta:
        verbose_name = '禁止IP列表'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
