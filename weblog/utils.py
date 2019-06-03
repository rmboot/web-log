import logging

logger = logging.getLogger(__name__)


def send_email(emailto, title, content):
    from weblog.log_signals import send_email_signal
    send_email_signal.send(send_email.__class__, emailto=emailto, title=title, content=content)


def block_ip(ip_addr):
    from weblog.log_signals import block_ip
    block_ip.send(block_ip.__class__, ip_addr=ip_addr)


def unblock_ip(ip_addr):
    from weblog.log_signals import unblock_ip
    unblock_ip.send(unblock_ip.__class__, ip_addr=ip_addr)
