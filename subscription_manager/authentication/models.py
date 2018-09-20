# Django imports
from django.db import models
from django.conf import settings
from django.contrib.auth import get_backends, get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone

# Application imports
from .managers import TokenManager


class Token(models.Model):
    """
    Token model.
    """
    # Fields
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Leser_in'
    )
    action = models.CharField(
        'Typ',
        max_length=6,
        choices=(
            ('signup', 'Bestätigungs-Token'),
            ('login', 'Login-Token')
        )
    )
    code = models.CharField(
        'Code',
        max_length=100,
        unique=True,
        editable=False
    )
    valid_until = models.DateTimeField(
        'gültig bis'
    )
    sent_at = models.DateTimeField(
        'gesendet am',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Custom model manager
    objects = TokenManager()

    def __str__(self):
        return 'Token({}, {})'.format(self.user.email, self.code)

    def is_valid(self):
        """
        True if the token is still valid.
        """
        return timezone.now() <= self.valid_until

    def is_expired(self):
        """
        True if the token is expired.
        """
        return not self.is_valid()

    @staticmethod
    def b64_encoded(email):
        """
        Encodes a given input with url safe base64.
        """
        return urlsafe_base64_encode(force_bytes(email)).decode()

    @staticmethod
    def b64_decoded(email_b64):
        """
        Decodes a url safe base64 encoded input.
        """
        try:
            return force_text(urlsafe_base64_decode(email_b64))
        except DjangoUnicodeDecodeError:
            return None
        except ValueError:
            return None

    @staticmethod
    def url(email, code):
        """
        Returns the url for a given email address and code.
        Example: https://hostname.tld/auth/token/cmVkYWt0aW9uQHpzLW9ubGluZS5jaA/1836af19-67df-4090-8229-16ed13036480/
        """
        return '{}{}'.format(
            settings.BASE_URL,
            reverse(
                'token_verification',
                kwargs={
                    'email_b64': Token.b64_encoded(email),
                    'code': code
                }
            )
        )

    def send(self, code, next_page=None):
        """
        Sends the token code with each backend that has a
        send method defined and updates sent_at field.
        """
        # Send token
        for backend in get_backends():
            if hasattr(backend, 'send'):
                backend.send(self, code, self.action, next_page)
        # Update sent_at field
        self.sent_at = timezone.now()
        self.save()
