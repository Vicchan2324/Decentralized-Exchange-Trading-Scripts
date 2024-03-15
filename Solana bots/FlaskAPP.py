from flask import Flask, render_template
from flask_socketio import SocketIO
from NewPairTracker import run  
import asyncio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')  

async def detect_new_pairs():
    async for data in run():  
        socketio.emit('new_pair', data)  

if __name__ == '__main__':
    socketio.start_background_task(detect_new_pairs)
    socketio.run(app, debug=True)
