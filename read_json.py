import json
from db import Teachers, Teacher, Questions, Question, Sections, Course_Section, Course_Section_Meeting, Meetings

def read_json(file):
    with open("course-dump.json", 'r') as json_file:
        for line in json_file:
            dict = json.loads(line)
            subject = dict['Sub']
            level = dict['Lvl']
            name = dict['Title']
            section = dict['Sec']
            teacher_name = dict['Instructor']

            teacher_last_name = ""
            for i in teacher_name:
                if i != ' ':
                    teacher_last_name += i
                else:
                    break
            teacher_last_name = teacher_last_name.lower()

            new_teacher = Teacher(data={'name': teacher_last_name, '_id':None})
            Teachers.insert(teacher = new_teacher)

            new_course = Course_Section(data={'course':subject+level, 'section':section, '_id': None, 'name' : name, 'teacher_name': teacher_last_name, 'teacher_id' : new_teacher.getId()})
        
            print("inserted course %s" % new_course)

            Sections.insert_one(course_section = new_course)



if __name__ == '__main__':
    read_json("course-dump.json")