# Django imports
from django.db import models, IntegrityError
from django.utils.crypto import get_random_string


class PaymentManager(models.Manager):
    """
    Custom manager for payments.
    """
    def create(self, **obj_data):
        """
        Overrides the default create method. It generates a unique
        code with which the payment can be identified.
        """
        # Try creating unique code object
        while True:
            try:
                # Generate a code
                code = 'ZS-' + get_random_string(6).upper()
                # Try creating token object
                obj_data['code'] = code
                payment = super().create(**obj_data)
            except IntegrityError:
                continue
            break
        return payment
