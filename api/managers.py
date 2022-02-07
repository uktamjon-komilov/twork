from django.contrib.auth.models import UserManager as BaseUserManager
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    def create_user(self, phone=None, password=None):
        if not phone:
            raise ValueError(_("Phone number must be provided"))
        
        if not password:
            raise ValueError(_("Password must be provided"))
        
        user = self.model(phone=phone)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, phone, password):
        user = self.create_user(phone, password)
        user.is_superuser = True
        user.save()

        return user