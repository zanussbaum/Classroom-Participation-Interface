import re
import pprint
from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from random import getrandbits
from db import Teachers, Teacher, Questions, Question, Sections, Course_Section, Course_Section_Meeting, Meetings

"""
TODO:
    Create a way to input all the responses from a certain class --> database call, then put into {{}}
        in html  

    On teacher disconnect, the course meeting must be inserted into the our Meetings relation
"""

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)

people = {}
which_room = {}
question_id = {}
meeting_id = {}
questions_list = []

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        course_tuple = request.form['course'].split(" ")

        person = request.form['person']
        course = course_tuple[0]
        section = course_tuple[1]
        teacher = course_tuple[2]

        #Grab the teacher object based off the name of the teacher
        current_teacher = Teachers.find_one({"name" : teacher})
        
        #Grab the Section object based off the department, course, section, name and the teacher object
        try:
            current_section = Sections.find_one(query={"course": course, "section": section, "teacher_name" : teacher})
        except Exception as ex:
            print("current_section")
            print(str(ex))

        class_number = Meetings.find_all_meetings(section  = current_section)

        if person == 'teacher':
            #Create a new meeting object, and set the class number to be the number we just calculated
            try:
                current_meeting = Course_Section_Meeting({'session_number': class_number, 'course_section': current_section})
            except Exception as ex:
                print("current_meeting")
                print(str(ex))

            #Insert the new meeting into our Meetings Table
            try:
                hash = getrandbits(128)
                url = strip_url(url_for('teacher', teacher=teacher, course=course, section=section, class_number=class_number, hash=hash),False)
                if url in meeting_id:
                    Meetings.insert_and_increment(meeting_id[url])
                else:
                    Meetings.insert_one(current_meeting)
                    meeting_id[url] = current_meeting.id

            except Exception as ex:
                print("Meetings insertion")
                print(str(ex))

            return redirect(url_for('teacher', teacher=teacher, course=course, section=section, class_number=class_number, hash=hash))

        else:
            return redirect(url_for('student', teacher=teacher, course=course, section=section, class_number=class_number))
    courses = Sections.find()
    return render_template('home.html',courses=courses)
    
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
def teacher(teacher,course, section, class_number, hash,methods=['GET', 'POST']):
    """Webpage routine for a teacher in a certain class on a certain day 

    Parameters:
        course: a certain class number i.e. CSC351
        section: section of the class
        class_number: the current class day
        hash: random hash generated for webpage

    Returns:
        render_template('teacher.html'): renders the template for new session
    """
    if request.method == 'POST':
        print(request)
    url = "teacher" + "/" + teacher + "/" + course + "/" + section + "/" + class_number
    previous_sessions = Meetings.find_one({"_id":meeting_id[url]})
    session = [s + 1 for s in range(previous_sessions['session_number']-1)]
    
    return render_template('teacher.html',session=session)


def strip_url(json, is_student):
    if is_student:
        url = json[json.find('student'):]
    else:
        url = json[json.find('teacher'):json.rfind('/')]

    return url

def extract_url(url):
    return url.split('/')

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

    url = strip_url(json['url'], True)
    url = url.replace('student','teacher')

    current_question = Questions.getOneQuestion(question_id[url])

    if current_question is not None:
        try:
            current_question.addResponse(json)
            Questions.insert_and_update(current_question,question_id[url])
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

    url_list = extract_url(url)

    #Try to create the new question, passing in the question text
    try:
        newQuestion = Question(json)
        questions_list.append(1)
        newQuestion.setQuestionNumber(counter = len(questions_list))
    except Exception as ex:
        print("question formation")
        print(str(ex))

    try:
        thisTeacher = Teachers.find_one({'name': url_list[1]})
        
    except Exception as ex:
        print(str(ex))

    thisTeacherId = thisTeacher.getId()

    try:  
        thisSection = Sections.find_one({'course': url_list[2], 'section': url_list[3], 'teacher_id' : thisTeacherId})
    except Exception as ex:
        print("find section")
        print(str(ex))
   
    
    try:
        Questions.insert_one(newQuestion)
        question_id[url] = newQuestion.getQuestionId()
    except Exception as ex:
        print("Question Insertion")
        print(str(ex))
    
   
    #Get the current meeting
    try:
        currentMeeting = Meetings.find_one({"course_section" : thisSection.to_dict()})
    except Exception as ex:
        print("find current meeting")
        print(str(ex))
    
    try:
        Meetings.insert_and_update(question_id[url], meeting_id[url])
    except Exception as ex:
        print("add question to meeting")
        print(str(ex))

    room = which_room.get(request.sid)

    socketio.emit('teacher question', json, callback=questionPosed,room=room)

@socketio.on('session request')
def session_request(json):
    url = strip_url(json['url'],False)
    session_number = json['session']

    if url in meeting_id:
        meeting = Meetings.find_one({"_id": meeting_id[url]})
        questions = []
        for id in meeting['questions'][int(session_number)-1]:
            this_question = Questions.getOneQuestion(id)
            questions.append(this_question.to_dict())

    socketio.emit('questions',questions,room=which_room.get(request.sid))
        

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