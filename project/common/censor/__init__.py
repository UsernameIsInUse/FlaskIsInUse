from project.extensions import profanity
from project.common.censor.sub_string_block import data as sub_strings

def check_censor(s):
  for sub_string in sub_strings:
    if sub_string in s:
      return True
  return profanity.contains_profanity(s)