from flask import Flask, render_template, request, session, jsonify
from flask_cors import CORS
#import rclpy
import queue
app = Flask(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})
# class ROSNode(Node):
#     def __init__(self):
#         super().__init__('flask_ros_node')
#         self.publisher = self.create_publisher(String, 'ros_topic', 10)
# setup a rate to send messages sync the hz between the sent and the rates
#     def publish_message(self, message):
#         msg = String()
#         msg.data = message
#         self.publisher.publish(msg)
#         self.get_logger().info(f"Message published to ROS: {message}")
@app.route('/')
def hello():
    return render_template('index.html')


def sendDataToROS(location):
    # label based on recieve
    # 1, 2, 3
    # int or xyz or string, 
    # from the payload get data
    # # ROS Communication
    # rclpy.init()
    # node = ROSNode()
    # node.publish_message(location)
    # rclpy.shutdown()
    print("Data sent to ROS\n")
    return

@app.route('/request', methods=['POST'])
def requestReceived():
    startLocation = request.json.get('startLocation')
    endLocation = request.json.get('endLocation')
    itemToSend = request.json.get('item')
    sendDataToROS(startLocation)
    data = {
        'item': itemToSend
    }
    if 'locations_queue' not in session:
        session['locations_queue'] = queue.Queue()  # Create a new queue if it doesn't exist in the session
    session['locations_queue'].put(endLocation)  # Add the end location to the queue
    # add vue to the route and then route to the html file that has the progress bar
    # connect this with a jinja template that is the same as the vue template
    print('Request received successfully')
    return jsonify(data)

# create an axios request that sends this information to the backend server
@app.route('/send', methods=['POST'])
def returnButtonPushed():
    data = {'locationSent': False}
    if 'locations_queue' in session:
        locations_queue = session['locations_queue']
        if not locations_queue.empty():
            location = locations_queue.get()  # Retrieve the location from the queue
            data['location'] = True
    sendDataToROS(location)
    return jsonify(data)
