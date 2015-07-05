import logging

from . import base


logger = logging.getLogger(__name__)


class UserManager(base.Manager):
    URL_KEY = 'USER'

class User(base.Model):
    ''' A User '''
    class Meta:
        manager = UserManager


class GroupManager(base.Manager):
    URL_KEY = 'GROUP'


class Group(base.Model):
    class Meta:
        manager = GroupManager
