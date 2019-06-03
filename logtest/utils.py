from weblog.utils import send_email

import logging

logger = logging.getLogger(__name__)


def send_comment_email(subject, comment, log_info):
    try:
        site = 'your site domain'
        subject = subject
        url = "https://{site}".format(site=site)
        html_content = '网址:%s <br /> %s <br /> %s' % (url, comment, log_info)
        tomail = 'your email addr'
        send_email([tomail], subject, html_content)
    except Exception as e:
        logger.error(e)
