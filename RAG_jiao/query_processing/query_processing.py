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

def expand_subject_abbreviation(text):
    import re
    subject_abbr_dict = {}
    subject_abbr_dict['CSSE'] = ' Computer Science and Software Engineering CSSE'
    subject_abbr_dict['CS'] = ' Computer Science CS'
    subject_abbr_dict['DS'] = ' Data Science CS'
    subject_abbr_dict['BE'] = ' Biomedical Engineering BE'
    subject_abbr_dict['ME'] = ' Mechanical Engineering ME'
    subject_abbr_dict['BMTH'] = ' Biomathematics BMTH'
    subject_abbr_dict['CHEM'] = ' Chemistry CHEM'
    subject_abbr_dict['BIO'] = ' Biology BIO'
    subject_abbr_dict['CHE'] = ' Chemical Engineering CHE'
    subject_abbr_dict['CPE'] = ' Computer Engineering CPE'
    subject_abbr_dict['CE'] = ' Civil Engineering CE'
    subject_abbr_dict['SE'] = ' Software Engineering SE'
    subject_abbr_dict['ECE'] = ' Electrical Engineering ECE'
    subject_abbr_dict['ENGD'] = ' Engineering Design ENGD'
    subject_abbr_dict['EMGT'] = ' Engineering Management EMGT'
    subject_abbr_dict['EM'] = ' Engineering Mechanics EM'
    subject_abbr_dict['ES'] = ' Engineering Science ES'
    subject_abbr_dict['ESL'] = ' English as second language EM'
    subject_abbr_dict['MA'] = ' Mathematics EM'
    subject_abbr_dict['Math'] = ' Mathematics Math'
    subject_abbr_dict['ME'] = ' Mechanical Engineering ME'
    subject_abbr_dict['EP'] = ' NanoEngineering nano engineering EP'
    subject_abbr_dict['OE'] = ' Optical Engineering OE'
    subject_abbr_dict['PH'] = ' Physics PH'
    subject_abbr_dict['AI'] = ' Artifical Intelligence AI'

    reg_exp = '\\sCSSE'
    for k in subject_abbr_dict.keys():
        if (k == 'CSSE'):
            continue
        reg_exp += f'|\\s{k}'
    # Build a reg exp that detects abbr.
    
    def repl_cb(match):
        # match = match.string
        match = match.group(0)
        match = match.strip()
        print(match)
        return subject_abbr_dict[match]

    import re
    print(reg_exp)
    return re.sub(reg_exp, repl_cb, text)
    
