from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

from flask_migrate import Migrate
migrate = Migrate(render_as_batch=True)

from flask_login import LoginManager
login = LoginManager()

from flask_wtf import CSRFProtect
csrf = CSRFProtect()

from flask_admin import Admin
admin = Admin(name="Admin", url="/admin/")

from flask_ipban import IpBan
ipban = IpBan()

from flask_flashy import Flashy
flashy = Flashy()

from flask_squeeze import Squeeze
squeeze = Squeeze()

from flask_mail import Mail
mail = Mail()

from flask_smorest import Api
api = Api()

from authlib.integrations.flask_client import OAuth
oauth = OAuth()

from better_profanity import profanity
from project.common.censor import the_big_username_blocklist
list = the_big_username_blocklist.data
list.append('flaskisinuse')
profanity.load_censor_words()
profanity.add_censor_words(list)
