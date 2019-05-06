import re
from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room
from random import getrandbits


"""
TODO:
    Create a way to input all the respones from a certain class --> database call, then put into {{}}
        in html  

    Make UI look better lol --> ask if this is necessary 
"""
app = Flask(__name__)
socketio = SocketIO(app)

people = {}
which_room = {}

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        teacher = request.form['teacherName']
        course = request.form.get('course')
        section = request.form.get('section')
        person = request.form.get('person')
        print(person)

        #this is where we would make a database call to see class number
        class_number = 1

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
        section: section o fthe class
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
        section: section o fthe class
        class_number: the current class day
        hash: random hash generated for webpage

    Returns:
        render_template('teacher.html'): renders the template for new session
    """

    #database call here to create class session 

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

    room = which_room.get(request.sid)
   

    socketio.emit('student response', json, callback=messageReceived,room=room)

@socketio.on('teacher question')
def teacher_question(json, methods=['GET', 'POST']):
    print('a teacher posed a question')

    #can parse json here to put into database   
    print(json)

    room = which_room.get(request.sid)

    socketio.emit('teacher question', json, callback=questionPosed,room=room)



@socketio.on('disconnect')
def disconnect():
    user = request.sid

    room = which_room.get(user)

    leave_room(room)

    people[room].remove(user)

    print("there are now %d users in %s" %(len(people[room]), room))


if __name__ == '__main__':
    socketio.run(app, debug=True)