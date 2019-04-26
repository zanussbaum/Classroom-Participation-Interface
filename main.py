from flask import Flask, render_template
from flask_socketio import SocketIO


"""
TODO:
    Be able to generate dynamic urls from homepage
        figure out why teacher webpage is not rendering correctly 

    Finish docstrings
"""
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def homepace():
    return render_template('home.html')
    
@app.route('/<string:course>/<int:section>/<int:class_number>/student')
def student(course, section, class_number):
    """Webpage routine for a student in a certain class on a certain day 

    Parameters:
        course: a certain class number i.e. CSC351
        section: section o fthe class
        class_number: the current class day

    Returns:
        render_template('student.html'): renders the template for new session 
    """
    return render_template('student.html')

@app.route('/teacher/<course>/<section>/<class_number>/<hash>')
def teacher(course, section, class_number, hash):
    """Webpage routine for a teacher in a certain class on a certain day 

    Parameters:
        course: a certain class number i.e. CSC351
        section: section o fthe class
        class_number: the current class day
        hash: random hash generated for webpage

    Returns:
        render_template('teacher.html'): renders the template for new session
    """
    return render_template('teacher.html')

def messageReceived(methods=['GET', 'POST']):
    print('student response was received!!!')

def questionPosed(methods=['GET', 'POST']):
    print('a teacher posed a question ')

@socketio.on('student response')
def student_response(json, methods=['GET', 'POST']):
    print('received a student response: ' + str(json))
    socketio.emit('student response', json, callback=messageReceived)

@socketio.on('teacher question')
def teacher_question(json, methods=['GET', 'POST']):
    print('a teacher posed a question')
    print(json)
    socketio.emit('teacher question', json, callback=questionPosed)


if __name__ == '__main__':
    socketio.run(app, debug=True)