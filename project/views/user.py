from flask import render_template, redirect, url_for, request
from flask_login import current_user, fresh_login_required
from project.views import bp
from project.access_control import user_check_decorator
from project.utils import send_email, log
from project.forms import EmailChangeForm
from project.models import User
from project import db
from flask_flashy import flash

@bp.route('/settings/', methods=['GET', 'POST'])
@fresh_login_required
def user_settings():
  email_form = EmailChangeForm()
  if email_form.validate_on_submit():
    user = User.query.filter_by(email=email_form.email.data).first()
    if current_user.email == email_form.email.data:
      flash('Submitted email is current email.', 'warning')
      log(user=current_user, request=request, description='Failed email change attempt')
    elif user:
      flash('Email already in use.', 'warning')
      log(user=current_user, request=request, description='Failed email change attempt')
    else:
      html = render_template("email/email_change.html", unsubscribe=False)
      subject = "Your vfolio Email Has Been Changed"
      send_email([current_user.email],subject,html)
      
      current_user.unconfirmed_email = email_form.email.data
      current_user.confirmed = False
      current_user.date_confirmed = None
      db.session.commit()
      log(user=current_user, request=request, description='Saved new email, needs re-confirmation')
      return redirect(url_for('views.confirm'))
  email_form = EmailChangeForm()
  return render_template('user/settings.html', email_form=email_form)