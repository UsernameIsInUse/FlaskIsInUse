from flask import redirect, url_for, request
from flask_login import current_user
from flask_flashy import flash

from project.views import bp
from project.utils import log

@bp.app_errorhandler(404)
def page_not_found(e):
  log(request=request, description=f'f"404 Error at {request.path}, Error: {e}"')
  flash('Page not found!', 'warning')
  return redirect(url_for('views.index'))


@bp.app_errorhandler(403)
def forbidden(e):
  log(request=request, description=f'f"403 Error at {request.path}, Error: {e}"')
  flash("You seem to be trying to do something you should not do!", 'danger')
  return redirect(url_for('views.index'))


@bp.app_errorhandler(500)
def internal_server_error(e):
  log(request=request, description=f'f"500 Error at {request.path}, Error: {e}"')
  flash('Whoops, something happened!', 'danger')
  return redirect(url_for('views.index'))