from flask import Flask, render_template
from flask_socketio import SocketIO


"""
TODO:
    Fix html/JS/JQuery scripts so that you get form data correctly 
"""
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def homepace():
    return render_template('home.html')
    
@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/teacher')
def teacher():
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
    socketio.emit('teacher question', json, callback=questionPosed)


if __name__ == '__main__':
    socketio.run(app, debug=True)