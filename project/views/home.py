from flask import render_template, redirect, url_for

from project.utils import reset_database
from project.access_control import admin_check_decorator
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

@bp.route('/support')
def support():
  return render_template('home/support.html')