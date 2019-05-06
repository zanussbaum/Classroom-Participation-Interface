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
    def __init__(self,data: str):
        self.data_dict = data if type(data) is dict else json.loads(data)
        self.name = self.data_dict.get("name")
        self.id = None

    def getName(self):
        return self.name

class _Teachers:
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
    def __init__(self, data: str):
        self.data_dict = data if type(data) is dict else json.loads(data)
        self.question = self.data_dict.get("text")
        self.map = {}
        self.id = None

    def setResponse(self, student, respose):
        if student not in self.map:
            self.map[student] = response

class _Questions:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["questions"]

    def getOneQuestion(self, query: dict) -> 'Question':
        item = self.collection.find_one(query)
        return None if item is None else Question(item)
    
    def getAllQuestions(self, query: dict) -> 'list(Question)':
        return (Question(item) for item in self.collection.getAllQuestions(query))

    def insert_one(self, question: 'Question') -> 'bson.ObjectId':
        obj_id = self.collection.insert_one(question.to_dict)
        question.id = obj_id.inserted_id
        return question


# Dict key 'teacher' here must be a teacher object 
class Course_Section(Teacher):
    def __init__(self, data: dict):
        self.code = data['code']
        self.professor_data = data['teacher']
        self.section = data['section']
        self.department = data['department']
        self.id = None

    def returnCourseSectionDetails(self,socket):
        temp = "Course Sections Details: " + self.code + " " + self.professor + " " + self.section + " " + self.department
        socket.send(temp)

class _Course_Sections:
    def __init__(self, data: dict):
        self.db = get_database()
        self.collection = self.db['course_sections']

    def insert_one(self, course_section : 'Course_Section') -> 'bson.ObjectId':
        obj_id = self.collection.insert_one()
        course_section.id = obj_id.inserted_id
    
    def getCourseByProfessor(self, teacher: 'Teacher') -> 'Course_Section':
        for i in self.collection:
            if i.professor_data.getName() == teacher.getName():
                #Not sure which one to send here 'socket' or 'return'
                socket.send(i)
                return i

class Course_Section_Meeting(Course_Section, Question, Teacher):
    def __init__(self, course_section: 'Course_Section', question = []):
        self.session_number = None
        self.meeting_map = {}
        self.date = datetime.datetime.now()
        self.id = None

        self.course_section = course_section

        #setting map to map from a date to a list of questions
        if question is not None:
            self.meeting_map.put(self.date, question)

    def getSessionNumber(self):
        return self.session
    
    def getDate(self):
        return self.date

class _Course_Section_Meeting(Course_Section, Question, Teacher):
    def __init__(self, data: dict):
        self.db = get_database()
        self.collection = self.db['course_section_meetings']
    
    def insert_one(self, course_section_meeting: 'Course_Section_Meeting'):
        obj_id = self.collection.insert_one()
        course_section_meeting.session_number = obj_id.inserted_id
        return course_section_meeting

    def findByProfessor(self, teacher: 'Teacher'):
        for i in self.collection:
            if i.course_section.professor_data == teacher:
                socket.send(i)
                return i









