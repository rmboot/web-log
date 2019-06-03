import django.dispatch
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import os
import logging

logger = logging.getLogger(__name__)

send_email_signal = django.dispatch.Signal(providing_args=['emailto', 'title', 'content'])
block_ip = django.dispatch.Signal(providing_args=['ip_addr'])
unblock_ip = django.dispatch.Signal(providing_args=['ip_addr'])


@receiver(send_email_signal)
def send_email_signal_handler(sender, **kwargs):
    emailto = kwargs['emailto']
    title = kwargs['title']
    content = kwargs['content']

    msg = EmailMultiAlternatives(title, content, from_email=settings.DEFAULT_FROM_EMAIL, to=emailto)
    msg.content_subtype = "html"

    from servermanager.models import EmailSendLog
    log = EmailSendLog()
    log.title = title
    log.content = content
    log.emailto = ','.join(emailto)

    try:
        result = msg.send()
        print(result)
        log.send_result = result > 0
    except Exception as e:
        logger.error(e)
        log.send_result = False
    log.save()


@receiver(block_ip)
def block_ip_handler(sender, **kwargs):
    ip_addr = kwargs['ip_addr']

    res = os.system('sudo iptables -I INPUT -s %s -j DROP' % ip_addr)

    from servermanager.models import BlockIPLog
    if BlockIPLog.objects.filter(ip_addr=ip_addr):
        print(ip_addr+' 该IP已经禁止,请勿重复添加')
        return
    block_log = BlockIPLog()
    block_log.ip_addr = ip_addr
    try:
        result = res
        block_log.send_result = result == 0
    except Exception as e:
        logger.error(e)
        block_log.send_result = False
    block_log.save()


@receiver(unblock_ip)
def unblock_ip_handler(sender, **kwargs):
    ip_addr = kwargs['ip_addr']

    res = os.system('sudo iptables -D INPUT -s %s -j DROP' % ip_addr)

    from servermanager.models import BlockIPLog
    try:
        if res == 0:
            BlockIPLog.objects.filter(ip_addr=ip_addr).delete()
        else:
            raise Exception("解除IP禁止失败")
    except Exception as e:
        logger.error(e)
