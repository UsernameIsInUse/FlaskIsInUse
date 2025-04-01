from flask import request, send_from_directory
from project.views import bp
from project.models import User
from project.utils import log
import random

@bp.before_app_request
def log_page_view():
  """Logs each page view, except routes that are blocked for their own specific logging.
  """
  url = request.path
  blocked = [
    '/static',
    '/admin/static',
    '/load',
    '/api',
  ]
  for b in blocked:
    if url.startswith(b):
      return    
  log(request=request, description=f'Viewed {url}')
  
@bp.app_template_filter('shuffle')
def filter_shuffle(seq:list):
  """Shuffles a given list in jinja templating.

  Args:
      seq (list): _description_

  Returns:
      _type_: _description_
  """
  try:
    result = list(seq)
    random.shuffle(result)
    return result
  except:
    return seq
  
@bp.app_template_filter('order')
def filter_order(seq:list):
  """orders a given list by `.order()` in jinja templating.

  Args:
      seq (list): List to be sorted

  Returns:
      _type_: Sorted list
  """
  try:
    ul = list(seq)
    ol = sorted(ul,key=lambda li: li.order())
    return ol
  except:
    return seq

@bp.route('/favicon.ico')
def favicon():
  return send_from_directory(bp.static_folder, 'img/favicon.png')
