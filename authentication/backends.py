# Python imports
import hashlib

# Django imports
from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from .models import LoginToken


class TokenBackend(ModelBackend):
    def authenticate(self, request, email=None, code=None, **kwargs):
        try:
            encoded_code = hashlib.sha256(code.encode('utf-8')).hexdigest()
            token = LoginToken.objects.get(code=encoded_code)
            if token.is_valid():
                user = token.user
                if user.email == email:
                    token.delete()
                    if user.is_active:
                        return user
            return None
        except LoginToken.DoesNotExist:
            return None


class EmailTokenBackend(TokenBackend):

    def send(self, token, code):
        subject = 'Subject'
        to_email = [token.user.email]
        from_email = settings.EMAIL_FROM_ADDRESS

        context = {
            'to_name': token.user.first_name,
            'from_name': settings.NAME,
            'url': token.login_url(code),
            'code': code,
        }
        text_content = render_to_string('authentication/emails/token_email.txt', context)
        html_content = render_to_string('authentication/emails/token_email.html', context)

        message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        message.attach_alternative(html_content, 'text/html')

        message.send()
