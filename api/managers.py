from django.contrib.auth.models import UserManager as BaseUserManager
from django.utils.translation import gettext as _

from parler.managers import TranslatableManager, TranslatableQuerySet
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet


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


class CategoryQuerySet(TranslatableQuerySet, TreeQuerySet):

    def as_manager(cls):
        manager = CategoryManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager
    as_manager.queryset_only = True
    as_manager = classmethod(as_manager)


class CategoryManager(TreeManager, TranslatableManager):
    _queryset_class = CategoryQuerySet