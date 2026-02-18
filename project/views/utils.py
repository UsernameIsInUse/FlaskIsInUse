from flask import request, send_from_directory

from project.views import bp
from project.utils import log

import random

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
  from flask import Request

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
    '/_debug'
  ]
  for b in blocked:
    if url.startswith(b):
      return    
  log(request=request, description=f'Viewed {url}')
  
@bp.app_template_filter('shuffle')
def filter_shuffle(seq:List) -> List:
  """Shuffles a given list in jinja templating.

  Args:
      seq (List): List to shuffle.

  Returns:
      List: Shuffled list.
  """
  try:
    result = list(seq)
    random.shuffle(result)
    return result
  except:
    return seq
  
@bp.app_template_filter('order')
def filter_order(seq:List) -> List:
  """orders a given list by `.order()` in jinja templating.

  Args:
      seq (List): List to be ordered.

  Returns:
      List: Ordered list.
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
