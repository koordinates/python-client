import logging

from . import base


logger = logging.getLogger(__name__)


class UserManager(base.Manager):
    _URL_KEY = 'USER'


class User(base.Model):
    ''' Represents a Koordinates User '''
    class Meta:
        manager = UserManager


class GroupManager(base.Manager):
    _URL_KEY = 'GROUP'


class Group(base.Model):
    ''' Represents a Koordinates Group '''
    class Meta:
        manager = GroupManager
