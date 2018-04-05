# Python imports
import hashlib
import uuid

# Django imports
from django.db import models, IntegrityError
from django.conf import settings
from django.utils import timezone


class LoginTokenManager(models.Manager):
    """
    Custom manager for login tokens.
    """

    def create(self, **obj_data):
        """
        Overrides the default create method. It sets the valid_until
        attribute and generates a random code.
        """
        # Set token expiration
        obj_data['valid_until'] = timezone.now() + settings.TOKEN_EXPIRATION

        # Try creating LoginToken object
        while True:
            try:
                # Generates a UUID
                code = uuid.uuid4()
                # Hash UUID with SHA256
                encoded_code = hashlib.sha256(str(code).encode('utf-8')).hexdigest()
                # Try creating token object
                obj_data['code'] = encoded_code
                token = super().create(**obj_data)
            except IntegrityError:
                continue
            break
        return code, token

    def create_and_send(self, **obj_data):
        """
        Creates and sends a token object.
        """
        # Create and send token
        code, token = self.create(**obj_data)
        token.send(code)
        return token

    def all_expired(self):
        """Selects all tokens that have been sent more than seven days ago"""
        return self.filter(
            sent_at__lt=timezone.now() - settings.TOKEN_EXPIRATION
        )

    def delete_all_expired(self):
        self.all_expired().delete()
