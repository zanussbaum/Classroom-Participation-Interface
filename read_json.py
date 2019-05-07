import json
from db import Sections,Meetings, Teacher, Course_Section, Course_Section_Meeting

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
            course_meeting = Course_Section_Meeting(course_section=course)

            print("inserted course %s" %course)

            Sections.insert_one(course)
            Meetings.insert_one(course_meeting)



if __name__ == '__main__':
    read_json("course-dump.json")