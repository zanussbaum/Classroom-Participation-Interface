import datetime
import json
from pymongo import MongoClient

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DATABASE = "VirtualClassroom"
MONGO_CLIENT = client = MongoClient(MONGO_HOST,MONGO_PORT)

def get_database() -> 'pymongo.database.Database':
    return MONGO_CLIENT.get_database(MONGO_DATABASE)

class Teacher:
    def __init__(self, data: dict):
        self.name = data['name']

        if data['_id'] is None:
            self.id = None
        else:
            self.id = data['_id']

    def getName(self):
        return self.name
    
    def getId(self):
        return self.id

    def to_dict(self):
        _return = dict(name = self.name)
        return _return if self.id is None else _return.update({"_id": self.id})

class _Teachers(Teacher):
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["teachers"]
     
    #I believe we have to pass in all the information for a particular teacher here, not just the name
    def find_one(self, query: dict) -> 'Teacher':
        item = self.collection.find_one(query)
        return None if item is None else Teacher(item)

    def find(self, query: dict) -> list('Teachers'):
        return (Teacher(item) for item in self.collection.find(query))

    def insert(self, teacher: 'teacher'):
        obj_id = self.collection.insert_one(teacher.to_dict())
        teacher.id = obj_id.inserted_id
        return teacher

class Question:
    def __init__(self, data: dict):
        self.question = data['question']
        
        self.responses = {}

        self.number = None
            
        self.id = None

    def getQuestion(self):
        return self.question
    
    def getQuestionNumber(self):
        return self.number
    
    def getQuestionId(self):
        return self.id

    def getStudentResponses(self):
        return self.responses

    def setQuestionNumber(self, counter):
        self.number = counter
       

    def addResponse(self, data: dict):
        if data['user_name'] not in self.responses:
            self.responses[data['user_name']] = data['message']
            
    def to_dict(self):
        _return = dict(question=self.question, responses = self.responses, number = self.number)
        # _return['responses'] = self.responses
        return _return if self.id is None else _return.update({"_id": self.id})
    

class _Questions(Question):
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["questions"]

    def getOneQuestion(self, query: dict) -> 'Question':
        id = query['question']
        item = self.collection.find_one({"_id" : id})
        return None if item is None else Question(item)
    
    def getAllQuestions(self, query: dict) -> 'list(Question)':
        return (Question(item) for item in self.collection.getAllQuestions(query))

    def insert_one(self, question: 'Question') -> 'bson.ObjectId':
        obj_id = self.collection.insert_one(question.to_dict())
        question.id = obj_id.inserted_id
        return question



# Dict key 'teacher' here must be a teacher object 
class Course_Section(Teacher):
    def __init__(self, data: dict, teacher: 'Teacher'):
        #course "CSC353"
        self.course = data['course']
        #Section A
        self.section = data['section']
        
        #self.class_number = data['class_number']
        
        #Teacher object
        self.teacher = teacher

        if data['_id'] is None:
            self.id = None
        else:
            self.id = data['_id']

    def returnCourseSectionDetails(self):
        temp = "Course Sections Details: " + "\nProfessor: " + self.teacher.getName() + "\nCourse: " + self.course + "\nSection: " + self.section 
        return temp

    def getCourse(self):
        return self.course
    
    def getSection(self):
        return self.section

    def getProfData(self):
        return self.teacher

    def getId(self):
        return self.id

    def to_dict(self):
        _return = dict(course= self.course, section = self.section, teacher = self.teacher.to_dict())
        return _return if self.id is None else _return.update({'_id': self.id})

class _Course_Sections(Course_Section,Teacher):
    def __init__(self):
        self.db = get_database()
        self.collection = self.db['course_sections']

    def insert_one(self, course_section : 'Course_Section') -> 'bson.ObjectId':
        obj_id = self.collection.insert_one(course_section.to_dict())
        course_section.id = obj_id.inserted_id
    
    def getCourseByProfessor(self, teacher: 'Teacher') -> 'Course_Section':
        for i in self.collection.find():
            if i['professor_data'].getName() == teacher.getName():
                return i.getId()

    def setClassNumber(self, teacher, course, section):
        class_number = 1

        for i in self.collection.find():
            if course == i['course']:
                if section == i['section']:
                    if i['teacher'] is None:
                        return class_number
                    else:
                        if teacher == i['teacher'].getName():
                            class_number+=1

        return class_number

    def returnTeacher(self, name):
        for i in self.collection.find():
            if i['teacher'] is None:
                return None
            else:
                return i['teacher'].getName()

class Course_Section_Meeting(Course_Section, Question, Teacher):
    def __init__(self, course_section: 'Course_Section'):
        self.questions = []
        self.date = datetime.datetime.now()
        self.id = None
        self.session_number = 1
        self.course_section = course_section

    def setSessionNumber(self, number):
        self.session_number = number
        
    #adding questions to a question list
    def addQuestion(self, question: 'Question'):
        if question is not None:
            self.questions.append(question)
            
    def getSessionNumber(self):
        return self.session_number
    
    def getDate(self):
        return self.date
    
    def getId(self):
        return self.id

    def getCourseSection(self):
        return self.course_section

    def to_dict(self):
        _return = dict(questions= self.questions, date = self.date, course_section = self.course_section.to_dict(), session_number = self.session_number)
        return _return if self.id is None else _return.update({"_id" : self.id})

class _Course_Section_Meetings(Course_Section, Question, Teacher):
    def __init__(self):
        self.db = get_database()
        self.collection = self.db['course_section_meetings']
    
    def insert_one(self, course_section_meeting: 'Course_Section_Meeting'):
        obj_id = self.collection.insert_one(course_section_meeting.to_dict())
        course_section_meeting.id = obj_id.inserted_id
        return course_section_meeting

    def find_one(self, query:dict):
        id = query['meeting']
        item = self.collection.find_one({'_id': id})
        return None if item is None else Course_Section_Meeting(item)

    def findByProfessor(self, teacher: 'Teacher'):
        for i in self.collection.find():
            if i.course_section.professor_data == teacher:
                return i
   
    def getNumSessions(self, section: 'Course_Section'):
        number = 0
        for i in self.collection.find():
            if section == i['course_section_meeting'].getCourseSection():
                number += 1
        return number

    def output(self) -> 'list of meetings':
        output = []
        for i in self.collection.find():
            output.append(i)
        return output
                
Teachers = _Teachers()
Questions = _Questions()
Sections = _Course_Sections()
Meetings = _Course_Section_Meetings()








