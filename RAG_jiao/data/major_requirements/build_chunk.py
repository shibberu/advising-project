'''
This code builds chunks from major requirements files under a sub-directory of ./processed.
This code should be called after rename_processed_files
'''
if __name__ == "__main__":
  import os
  p = "./processed/manually_processed/"
  with open('./major_req_info.txt', 'w') as chunk_f:
    for f in os.listdir(p):
      f_path = p + f
      file_content = None
      with open(f_path, 'rb') as f_reader:
        file_content = str(f_reader.read())
        file_content = file_content.replace("\"", "").replace("\'", "")
        inject = None
        major_name = f.split('.csv')[0].replace("_", " ").lower()
        if ('second_major' in f.lower()):
          inject = f"{major_name} is for second major only. Here is the csv that describes the required courses for {major_name}: "    
        else:
          #inject = f"The following is a csv file describing the requirements for majoring in {major_name}. All courses on the list are required if {major_name} is declared as a first major. If a course comes with an X, has an X next to it, or has an X on its row, that course is required if {major_name} is declared as a second major. If a course does not come with an X, does not have an X next to it, does not have an X on its row, the course is required if {major_name} is declared as a first major, but is not required if {major_name} is declared as a second major. Here is the csv that describes the required courses for {major_name}: "
          inject = f"Here is the csv that describes the required courses for {major_name}: "
        chunk_f.write(f"""{{"source": "{f}", "text": "{inject}{file_content}", "lemma": "{inject}{file_content}"}}\n""")
    
