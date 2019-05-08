import datetime
import json
from pymongo import MongoClient

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DATABASE = "VirtualClassroom"
MONGO_CLIENT = client = MongoClient(MONGO_HOST,MONGO_PORT)

def get_database() -> 'pymongo.database.Database':
    MONGO_CLIENT.drop_database(MONGO_DATABASE)
    return MONGO_CLIENT.get_database(MONGO_DATABASE)

class Teacher:
    def __init__(self, data: dict):
        self.name = data['name']

        if data['_id'] is None:
            self.id = None
        else:
            self.id = data['_id']

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.__str__()

    def getName(self):
        return self.name
    
    def getId(self):
        return self.id

    def to_dict(self):
        _return = dict(name = self.name)
        return _return if self.id is None else _return.update({"_id": self.id})
    
    

class _Teachers():
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["teachers"]
     
    #I believe we have to pass in all the information for a particular teacher here, not just the name
    def find_one(self, query: dict) -> 'Teacher':
        for i in self.collection.find():
            if i['name'] == query['name']:
                return Teacher(i)

    def find(self, query: dict) -> list('Teachers'):
        return (Teacher(item) for item in self.collection.find(query))

    def insert(self, teacher: 'teacher'):
        obj_id = self.collection.insert_one(teacher.to_dict())
        teacher.id = obj_id.inserted_id
        return teacher

class Question:
    def __init__(self, data: dict):
        self.question = data['question']
        
        self.responses = None

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
        if self.responses == None:
            self.responses = {}
            if data['user_name'] not in self.responses:
                self.responses[data['user_name']] = data['message']
        else:
            if data['user_name'] not in self.responses:
                self.responses[data['user_name']] = data['message']
            
    def to_dict(self):
        _return = dict({"question":self.question, "responses":self.responses, "number":self.number})
        # _return['responses'] = self.responses
        return _return if self.id is None else _return.update({"_id": self.id})
    

class _Questions():
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
    def __init__(self, data: dict):
        #course "CSC353"
        self.course = data['course']

        #Section A
        self.section = data['section']
        
        #Title
        self.title = data['name']

        #Teacher Id 
        self.teacher_id = data['teacher_id']

        #teacher name for querying
        self.teacher_name = data['teacher_name']
        
        self.id = None
        
    def __str__(self):
        str = self.course + " " + self.section + " " + self.teacher.__str__()
        return str

    def __repr__(self):
        return self.__str__()

    def returnCourseSectionDetails(self):
        temp = "Course Sections Details: " + "\nProfessor: " + self.teacher.getName() + "\nCourse: " + self.course + "\nSection: " + self.section 
        return temp

    def getCourse(self):
        return self.course
    
    def getSection(self):
        return self.section

    def getId(self):
        return self.id
    
    def getTeacherId(self):
        return self.teacher_id
    
    def getTeacherName(self):
        return self.teacher_name

    def to_dict(self):
        _return = dict(name = self.title, course= self.course, section = self.section, teacher_name = self.teacher_name, teacher_id = self.teacher_id)
        return _return if self.id is None else _return.update({'_id': self.id})

class _Course_Sections():
    def __init__(self):
        self.db = get_database()
        self.collection = self.db['course_sections']

    def find(self, element=None):
        collection = self.collection
        if element is None:
            return collection.find({}, {"_id":0}).sort([("course",1)])
        else:
            return collection.find(element)
        
    def insert_one(self, course_section : 'Course_Section') -> 'bson.ObjectId':
        obj_id = self.collection.insert_one(course_section.to_dict())
        course_section.id = obj_id.inserted_id
    
    def getCourseByProfessor(self, teacher: 'Teacher') -> 'Course_Section':
        for i in self.collection.find():
            if i['professor_data'].getName() == teacher.getName():
                return i.getId()

    def find_one(self, query: dict) -> 'Course_Section':
        item = self.collection.find_one(query)
        return None if item is None else Course_Section(item)

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
    def __init__(self, data: dict):
        self.questions = None
        self.date = datetime.datetime.now()
        self.id = None
        self.session_number = data['session_number']
        self.course_section_id = data['course_section_id']

    def setSessionNumber(self, number):
        self.session_number = number
        
    #adding questions to a question list
    def addQuestion(self, question: 'Question'):
        if self.questions is None:
            if question is not None:
                self.questions  = []
                self.questions.append(question.getQuestionId())
        else:
            if question is not None:
                self.questions.append(question.getQuestionId())
                

    def getSessionNumber(self):
        return self.session_number
    
    def getDate(self):
        return self.date
    
    def getId(self):
        return self.id

    def getCourseSection(self):
        return self.course_section_id

    def to_dict(self):
        _return = dict(questions=self.questions, date = self.date, course_section_id = self.course_section_id, session_number = self.session_number)
        return _return if self.id is None else _return.update({"_id" : self.id})

class _Course_Section_Meetings():
    def __init__(self):
        self.db = get_database()
        self.collection = self.db['course_section_meetings']
    
    def insert_one(self, course_section_meeting: 'Course_Section_Meeting'):
        obj_id = self.collection.insert_one(course_section_meeting.to_dict())
        course_section_meeting.id = obj_id.inserted_id
        return course_section_meeting

    def find_one(self, data: dict):
        item = self.collection.find_one(data)
        return Course_Section_Meeting(item)

        
    def find_all_meetings(self, section: 'Course_Section_Meeting'):
        num_meetings = 1
        #section_name = section.getName()
        for i in self.collection.find():
            if section.getId() == i['course_section_id']:
                num_meetings+=1
        return num_meetings

    def findByProfessor(self, teacher: 'Teacher'):
        for i in self.collection.find():
            if i.course_section.professor_data == teacher:
                return i
   
    def getNumSessions(self, section: 'Course_Section'):
        number = 1
        for i in self.collection.find():
            if section == i['course_section']:
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








