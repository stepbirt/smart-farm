import time
import webapp2_extras.appengine.auth.models

from google.appengine.ext import ndb

from webapp2_extras import security

class User(webapp2_extras.appengine.auth.models.User):
  def set_password(self, raw_password):
    """Sets the password for the current user

    :param raw_password:
        The raw password which will be hashed and stored
    """
    self.password = security.generate_password_hash(raw_password, length=12)

  @classmethod
  def get_by_auth_token(cls, user_id, token, subject='auth'):
    """Returns a user object based on a user ID and token.

    :param user_id:
        The user_id of the requesting user.
    :param token:
        The token string to be verified.
    :returns:
        A tuple ``(User, timestamp)``, with a user object and
        the token timestamp, or ``(None, None)`` if both were not found.
    """
    token_key = cls.token_model.get_key(user_id, subject, token)
    user_key = ndb.Key(cls, user_id)
    # Use get_multi() to save a RPC call.
    valid_token, user = ndb.get_multi([token_key, user_key])
    if valid_token and user:
        timestamp = int(time.mktime(valid_token.created.timetuple()))
        return user, timestamp

    return None, None


class Farmdb(ndb.Model):
    id = ndb.StringProperty(required=True)
    user = ndb.StringProperty(required=True)
    numberCrayfish = ndb.IntegerProperty(default=0)
    nameFarm=ndb.StringProperty(default="")
    floor =ndb.IntegerProperty(default=0)
    wide = ndb.IntegerProperty(default=0)
    timeEatDay= ndb.IntegerProperty(default=0)
    temp = ndb.IntegerProperty(default=0)
    macPi= ndb.StringProperty(required=True)
    idArduino = ndb.StringProperty(repeated=True)
    timeWater = ndb.IntegerProperty(default=0)
    timeCreate = ndb.DateTimeProperty(auto_now_add=True) #datetime.now()

class Tempdb(ndb.Model):
    idFarm = ndb.StringProperty(required=True)
    temp = ndb.FloatProperty(required=True)
    time = ndb.DateTimeProperty(auto_now_add=True)
    day = ndb.DateTimeProperty(required=True)

class DayTempdb(ndb.Model):
    idFarm = ndb.StringProperty(required=True)
    day = ndb.DateTimeProperty(required=True)

class Changedb(ndb.Model):
    macPi= ndb.StringProperty(required=True)
    change= ndb.BooleanProperty(default=False)

class Notificationdb(ndb.Model):
    user = ndb.StringProperty(required=True)
    idFarm = ndb.StringProperty(required=True)
    countdownChangeWater = ndb.IntegerProperty(default=-1)
    temperature = ndb.FloatProperty(default=-1)
    statusFeed = ndb.StringProperty(default='') # g r y
    countdownFeeder = ndb.IntegerProperty(default=-1)
    time = ndb.DateTimeProperty(auto_now_add=True)
    nowFeeder=ndb.BooleanProperty(default=False)
    nowChangeWater=ndb.BooleanProperty(default=False)
    statusChangewatersystem = ndb.BooleanProperty(default=False)
    statusFeedersystem = ndb.BooleanProperty(default=False)
    statusCoolersystem = ndb.BooleanProperty(default=False)