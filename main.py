from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO
from random import getrandbits


"""
TODO:
    Create a way to input all the respones from a certain class 

    Make UI look better lol 
    About page/homepage
"""
app = Flask(__name__)
socketio = SocketIO(app)

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

def messageReceived(methods=['GET', 'POST']):
    print('student response was received!!!')

def questionPosed(methods=['GET', 'POST']):
    print('a teacher posed a question ')

@socketio.on('student response')
def student_response(json, methods=['GET', 'POST']):
    print('received a student response: ' + str(json))
    #can parse json here to store into database

    socketio.emit('student response', json, callback=messageReceived)

@socketio.on('teacher question')
def teacher_question(json, methods=['GET', 'POST']):
    print('a teacher posed a question')
    print(json)
    #can parse json here to put into database   
    socketio.emit('teacher question', json, callback=questionPosed)

if __name__ == '__main__':
    socketio.run(app, debug=True)