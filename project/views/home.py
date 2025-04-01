from flask import render_template, redirect, url_for, request
from project.utils import reset_database, admin_check_decorator
from project.views import bp

@bp.route('/')
def index():
  return render_template('home/index.html')

@bp.route('/reset')
@admin_check_decorator
def reset():
  reset_database(dev=True)
  return redirect(url_for('views.index'))

@bp.route('/tos')
def tos():
  return render_template('home/tos.html')

@bp.route('/privacy')
def privacy():
  return render_template('home/privacy.html')