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
        course_tuple = request.form['course'].split(" ")
        print(course_tuple)

        person = request.form['person']
        course = course_tuple[0]
        section = course_tuple[1]
        teacher = course_tuple[2]

        

        #this is where we would make a database call to see class number
        class_number = 1
        if person == 'teacher':
            #Grab the teacher object based off the name of the teacher
            current_teacher : 'Teacher'
            current_teacher = Teachers.find_one({"name" : teacher})
            
            
            #If the teacher isn't in our database, add it to the database
            # if current_teacher is None: # 'Add the teacher to the DB'
            #     print("add")
            #     current_teacher = Teacher(data={"name": teacher})
            #     Teachers.insert(teacher = current_teacher)
            
            #Grab the Section object based off the department, course, section, name and the teacher object
            current_section : 'Course_Section'
            try:
                current_section = Sections.find_one(query={"course": course, "section": section, "teacher_name" : teacher})
            except Exception as ex:
                print("current_section")
                print(str(ex))

            """
            #If the current section doesnt exist, then we havent added all the classes to the DB and we add it in here 
            if current_section is None: # 'Add the section to the DB'
                current_section = Course_Section(data={"course": course, "section": section, "_id" : None}, new_teacher = current_teacher)
                Sections.insert_one(course_section=current_section)
            """
            #Grab the object id's for future use, this part is tested and works correctly
            ids['teacher'] = current_teacher.getId()
            ids['section'] = current_section.getId()
            print(current_section.getId())
            

            """
            Set the class_number by iterating over the table of Meetings, and for each meeting 
            if the Section object is the same, we know that its a meeting and we increment the meeting number. 
            Once we have iterated over all the meetings, we return the class_number
            """
            class_number = Meetings.find_all_meetings(section  = current_section)

            #Create a new meeting object, and set the class number to be the number we just calculated
            try:
                current_meeting : 'Course_Section_Meeting'
                current_meeting = Course_Section_Meeting({'session_number': class_number, 'course_section_id': current_section.getId()})
                # class_number = Meetings.getNumSessions(section = current_section)
            except Exception as ex:
                print("current_meeting")
                print(str(ex))

            #Insert the new meeting into our Meetings Table
            try:
                Meetings.insert_one(course_section_meeting=current_meeting)
            except Exception as ex:
                print("Meetings insertion")
                print(str(ex))

            #Grab the object id for future use
            ids['meeting'] = current_meeting.getId()

        if person == 'teacher':
            hash = getrandbits(128)
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

    url = strip_url(json['url'],True)

    print(url)

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

    url_list = extract_url(url=url)

    # print("urlList")
    # for i in url_list:
    #     print(i)
    #Try to create the new question, passing in the question text
    try:
        newQuestion : 'Question'
        newQuestion = Question(data = json)
    except Exception as ex:
        print("question formation")
        print(str(ex))

    #questions is simply a list to keep track of the number of questions we have, it is a flask work around
    
    questions.append(1)

    #set the question number for this session
    newQuestion.setQuestionNumber(counter = len(questions))

    #finding the object id's for teacher
    thisTeacher : 'Teacher'
    try:
        
        thisTeacher = Teachers.find_one({'name': url_list[1]})
        
    except Exception as ex:
        print(str(ex))

    thisTeacherId = thisTeacher.getId()
    print(thisTeacherId)
    #finding the object id's for Section
    thisSection : 'Course_Section'
    try:  
        thisSection = Sections.find_one({'course': url_list[1], 'section': url_list[2], 'teacher_id' : thisTeacherId})
    except Exception as ex:
        print("find section")
        print(str(ex))
    print(thisSection.getCourse())
    print(thisSection.getSection())
    print(thisSection.getTeacherName())
    thisSectionId = thisSection.getId()
    print(thisSectionId)
    
    
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
    currentMeeting : 'Course_Section_Meeting'
    try:
        
        query = dict(session_number= url_list[4], course_section_id =thisSectionId)
        print(query)
        currentMeeting = Meetings.find_one({'session_number': url_list[4], "course_section_id" : thisSectionId})
    except Exception as ex:
        print("find current meeting")
        print(str(ex))
    print(currentMeeting.getCourseSection())

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