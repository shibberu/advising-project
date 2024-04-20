import ast
code_to_name_dict = {}
def build_code_to_name_dict():
  with open('./course_catalog.txt', 'r') as f:
    while True:
      line = f.readline()
      if len(line) == 0:
        break
      dict = ast.literal_eval(line)
      code_and_name = dict.get('text').split('\n')[0]
      code = code_and_name.split('-')[0][:-1]
      code_to_name_dict[code] = code_and_name
      code_to_name_dict[code.lower()] = code_and_name
      code_to_name_dict[code.lower().capitalize()] = code_and_name

      # code with no space
      code_no_space = ''.join(code.split(' '))
      code_to_name_dict[code_no_space] = code_and_name
      code_to_name_dict[code_no_space.lower()] = code_and_name
      code_to_name_dict[code_no_space.lower().capitalize()] = code_and_name

      for i in range(0, len(code_no_space)):
        if (code_no_space[i].isdigit()):
          mispell = ' '.join([code_no_space[0:i], code_no_space[i:len(code_no_space)]])
          code_to_name_dict[mispell] = code_and_name
          code_to_name_dict[mispell.lower()] = code_and_name
          code_to_name_dict[mispell.lower().capitalize()] = code_and_name
          break

import re
def expand_course_code_in_query(q, dict) :
  '''
  append full names to course codes in q 
  '''

  # 2-9 is just a random choice... I think the letter part cant be more than 5
  reg = '\\w{2,9}[ ]{0,1}\\w{0,1}\\d{3}'

  # replace course code by its value in dict
  def repl_cb(match):
    # match = match.string
    match = match.group(0)
    if match in dict:
      return dict[match]
    return match


  return re.sub(reg, repl_cb, q)
