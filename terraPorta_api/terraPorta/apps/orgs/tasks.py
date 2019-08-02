from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from celery import Task

from smtplib import SMTPException


MAIL = settings.EMAIL_HOST_USER


class UserInvitation(Task):

    def run(self, email, code, org, username=None):
        try:
            url = '/user_invitation/{}'.format(code)
            print(url)
            link = getattr(settings, "SITE_URL") + url
            if username:
                context = {
                    'username': username,
                    'link': link,
                    'org': org
                }
            else:
                context = {
                    'username': email,
                    'link': link,
                    'org': org
                }

            text_content = get_template('apps/orgs/email_user_invitation.txt').render(context)
            html_content = get_template('apps/orgs/email_user_invitation.html').render(context)

            subject = 'TerraPorta - Invitation'

            msg = EmailMultiAlternatives(subject, text_content, MAIL, [email, ])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except SMTPException:
            self.retry()
