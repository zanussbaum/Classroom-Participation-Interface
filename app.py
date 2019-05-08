import re
import pprint
from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from random import getrandbits
from db import Teachers, Teacher, Questions, Question, Sections, Course_Section, Course_Section_Meeting, Meetings

"""
Known Constraints:
    Teacher must log in before student
    Teacher must pose a question before any student submits a response
    Student responses will only be logged to the most recent question posed
"""

"""
TODO:
    Create a way to input all the responses from a certain class --> database call, then put into {{}}
        in html  

    On teacher disconnect, the course meeting must be inserted into the our Meetings relation

    Fix KeyError bugs, Disconnect Handler Errors, Message Handler Error. Terminal logs for my session are 
    included into the 'terminaldebuglog.txt' file
"""

app = Flask(__name__)
socketio = SocketIO(app)

people = {}
which_room = {}
ids = {}
questions = []

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        #may want to assert that prof name and student names are all lowercase to reduce duplicate entries into the db
        teacher = request.form['teacherName'].lower()
        course = request.form.get('course')
        section = request.form.get('section')
        person = request.form.get('person')
        

        #this is where we would make a database call to see class number
        class_number = 1
        """This logic is the only logic I am a bit unsure of, I will fix it in the morning. I confused
        the table names, so I just have to double check and make sure that it still works, I believe
        everything is fine

        """
        if person == 'teacher':
            class_number = Sections.setClassNumber(teacher=teacher,course=course,section=section)
            #if the class number is still one, it means that this is our first class and must be the first time for the teacher
            whichTeacher : 'Teacher'
            if class_number == 1:
                #insert a new teacher
                try:
                    data = {'name': teacher, '_id': None}
                    whichTeacher = Teacher(data=data)
                    Teachers.insert(whichTeacher)
                except Exception as ex:
                    print (str(ex))

            else:
                #find the teacher
                try:
                    whichTeacherDict = Sections.returnTeacher(name=teacher)
                    whichTeacher = Teachers.find_one(query = whichTeacherDict)
                except Exception as ex:
                    print (str(ex))

            #data dictionary declarations for session insertion
            tempDict = {}
            tempDict['course'] = course
            tempDict['section'] = section
            tempDict['_id'] = None

            #Creating a new Course_Section
            try:
                newClass : 'Course_Section'
                newClass = Course_Section(data=tempDict, teacher=whichTeacher)
            except Exception as ex:
                print ("newClass exception")
                print (str(ex))

            #Insert the newClass into our Sections relation
            try: 
                Sections.insert_one(course_section=newClass)
            except Exception as ex:
                print("insertion problem")
                print(str(ex))

            #Set the current section id to be the session we just added
            ids['section'] = newClass.getId()

            #Create a new meeting by passing in the newClass we just created
            try:
                newMeeting : 'Course_Section_Meeting'
                newMeeting = Course_Section_Meeting(course_section = newClass)
            except Exception as ex:
                print(str(ex))

            #set the Session Number to be the class number
            try:
                newMeeting.setSessionNumber(number = class_number)
            except Exception as ex:
                print(str(ex))

            #insert the new meeting into Meetings
            try:
                Meetings.insert_one(course_section_meeting=newMeeting)
            except Exception as ex:
                print(str(ex))
            
            ids['meeting'] = newMeeting.getId()

        if person == 'teacher':
            hash = getrandbits(128)
            return redirect(url_for('teacher', teacher=teacher, course=course, section=section, class_number=class_number, hash=hash))
        else:
            return redirect(url_for('student', teacher=teacher, course=course, section=section, class_number=class_number))
    
    return render_template('home.html')
    
@app.route('/student/<teacher>/<course>/<section>/<class_number>')
def student(teacher, course, section, class_number):
    """Webpage routine for a student in a certain class on a certain day 

    Parameters:
        course: a certain class number i.e. CSC351
        section: section of the class
        class_number: the current class day

    Returns:
        render_template('student.html'): renders the template for new session 
    """
    return render_template('student.html')

@app.route('/teacher/<teacher>/<course>/<section>/<class_number>/<hash>')
def teacher(teacher,course, section, class_number, hash, methods=['GET', 'POST']):
    """Webpage routine for a teacher in a certain class on a certain day 

    Parameters:
        course: a certain class number i.e. CSC351
        section: section of the class
        class_number: the current class day
        hash: random hash generated for webpage

    Returns:
        render_template('teacher.html'): renders the template for new session
    """
    
    return render_template('teacher.html')


def strip_url(json, is_student):
    if is_student:
        url = json[json.find('student'):]
    else:
        url = json[json.find('teacher'):json.rfind('/')]

    return url

@socketio.on('student connect')
def student_connection(json):
    student = request.sid
    # teacher, course, section  = handle_url(json['url'])
    print("student connection to url %s" %(json['url']))

    url = strip_url(json['url'], True)
    url = re.sub('student', '', url)

    join_room(url)

    people[url].append(student)

    which_room.update({student: url})

    print("%d people in the class %s" %(len(people[url]), url))

@socketio.on('teacher connect')
def teacher_connection(json):
    teacher = request.sid
    # url = handle_url
    print("teacher connection to url %s" %(json['url']))

    url = strip_url(json['url'], False)
    url = re.sub('teacher', '', url)

    join_room(url)

    people.update({url:[]})

    which_room.update({teacher: url})

    print("%d people in the class %s" %(len(people[url]), url))

def messageReceived(methods=['GET', 'POST']):
    print('student response was received!!!')

def questionPosed(methods=['GET', 'POST']):
    print('a teacher posed a question ')

@socketio.on('student response')
def student_response(json, methods=['GET', 'POST']):
    #can parse json here to store into database
    print('received a student response: ' + str(json))

    url = strip_url(json['url'],True)

    current_Question : 'Question'
    current_Question = Questions.getOneQuestion(query = ids)

    if current_Question is not None:
        try:
            current_Question.addResponse(data = json)
        except Exception as ex:
            print("Question addition")
            print(str(ex))
    else:
        print("Question has not been added")

    room = which_room.get(request.sid)
   

    socketio.emit('student response', json, callback=messageReceived,room=room)


@socketio.on('teacher question')
def teacher_question(json, methods=['GET', 'POST']):
    print('a teacher posed a question')

    url = strip_url(json['url'], False)

    #can parse json here to put into database   
    print(json)
    
    #Try to create the new question, passing in the question text
    try:
        newQuestion : 'Question'
        newQuestion = Question(data = json)
    except Exception as ex:
        print("question formation")
        print(str(ex))

    #questions is simply a list to keep track of the number of questions we have, it is a flask work around
    global questions
    questions.append(1)

    #set the question number for this session
    newQuestion.setQuestionNumber(counter = len(questions))

    """ Insert the finished question into the Questions relation
        ids['question'] holds the last question previously posed by the professor
        Assuming that a professor will only ask one question at a time, this allows us to 
        get the question and then add a response to it
    """
    try:
        Questions.insert_one(question=newQuestion)
        ids['question'] = newQuestion.getQuestionId()
    except Exception as ex:
        print("Question Insertion")
        print(str(ex))
    
    #Get the current meeting
    try:
        currentMeeting : 'Course_Section_Meeting'
        currentMeeting = Meetings.find_one(query = ids)
    except Exception as ex:
        print("find current meeting")
        print(str(ex))

    #Add the new Question to the current meeting relation
    try:
        currentMeeting.addQuestion(question = newQuestion)
    except Exception as ex:
        print("add question to meeting")
        print(str(ex))

    room = which_room.get(request.sid)

    socketio.emit('teacher question', json, callback=questionPosed,room=room)



@socketio.on('disconnect')
def disconnect():
    user = request.sid

    room = which_room.get(user)

    try:
        leave_room(room)
        people[room].remove(user)
    except ValueError:
        print("not in room")
        pass

    print("there are now %d users in %s" %(len(people[room]), room))


if __name__ == '__main__':
    socketio.run(app, debug=True)