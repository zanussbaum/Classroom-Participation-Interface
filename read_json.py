import json
from db import Sections, Teacher, Course_Section

def read_json(file):
    with open("course-dump.json", 'r') as json_file:
        for line in json_file:
            dict = json.loads(line)
            subject = dict['Sub']
            level = dict['Lvl']
            section = dict['Sec']
            teacher = dict['Instructor']
            teacher = Teacher(data={'name': teacher, '_id':None})
            course = Course_Section({'course':subject+level, 'section':section, '_id': None}, teacher)

            print("inserted course %s" %course)

            Sections.insert_one(course)



if __name__ == '__main__':
    read_json("course-dump.json")