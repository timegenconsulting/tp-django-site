from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User

from celery import Task

from smtplib import SMTPException


MAIL = settings.EMAIL_HOST_USER


class PasswordRecovery(Task):
    """
    Task sends password recovery mail to user.
    """

    def run(self, username, email, recovery_code):
        try:
            recovery_url = '/recovery_password/{}'.format(recovery_code)
            link = getattr(settings, "SITE_URL") + recovery_url

            context = {
                'username': username,
                'link': link
            }

            text_content = get_template('apps/accounts/email_password_recovery.txt').render(context)
            html_content = get_template('apps/accounts/email_password_recovery.html').render(context)

            subject = 'TerraPorta - reset password'

            msg = EmailMultiAlternatives(subject, text_content, MAIL, [email, ])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except SMTPException:
            self.retry()


class UsernameRecovery(Task):
    """
    Task sends email with username to user.
    """

    def run(self, username, email):
        try:
            context = {
                'username': username
            }

            text_content = get_template('apps/accounts/email_username_recovery.txt').render(context)
            html_content = get_template('apps/accounts/email_username_recovery.html').render(context)

            subject = 'TerraPorta'

            msg = EmailMultiAlternatives(subject, text_content, MAIL, [email, ])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except SMTPException:
            self.retry()


class UserActivation(Task):
    """
    Task sends activation code to user.
    """

    def run(self, username, email, code):
        try:
            active_url = '/user_activation/{}'.format(code)
            link = getattr(settings, "SITE_URL") + active_url

            context = {
                'username': username,
                'link': link
            }

            text_content = get_template('apps/accounts/email_user_activation.txt').render(context)
            html_content = get_template('apps/accounts/email_user_activation.html').render(context)

            subject = 'TerraPorta - User activation'

            msg = EmailMultiAlternatives(subject, text_content, MAIL, [email, ])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except SMTPException:
            self.retry()
