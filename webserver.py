import threading
from flask import Flask, render_template, request, session, jsonify
from flask_cors import CORS, cross_origin
# from flask_session import Session
from collections import deque # used for queuing tasks

from rclpy.node import Node
import rclpy
from std_msgs.msg import Int32
import secrets
import signal


# settings for sessions
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax'
)
app.secret_key = secrets.token_hex(32)

# enable CORS
# Session(app)
CORS(app)

# for ROS - comment out unless working on robot computer
class ROSNode(Node):
    def __init__(self):
        super().__init__('AppRequestNode')
        self.publisher = self.create_publisher(Int32, 'app_request_topic', 10)
        
# setup a rate to send messages sync the hz between the sent and the rates
    def send_int_location(self, location):
        msg = Int32()
        msg.data = location
        self.get_logger().info(f"Sending Loc to ROS {msg}")
        self.publisher.publish(msg)
        self.get_logger().info(f"Location sent to ROS {msg}")

def defineRobotLocation(location):
    robotLocation = 0
    if "V&V" in location:
        robotLocation = 1
    elif 'Demo' in location:
        robotLocation = 2
    elif 'Cafeteria' in location:
        robotLocation = 3
    return robotLocation

def ros_spin(node):
    rclpy.spin(node)

def sigint_handler(signal, frame):
    """
    SIGINT handler

    We have to know when to tell rclpy to shut down, because
    it's in a child thread which would stall the main thread
    shutdown sequence. So we use this handler to call
    rclpy.shutdown() and then call the previously-installed
    SIGINT handler for Flask
    """
    rclpy.shutdown()
    if prev_sigint_handler is not None:
        prev_sigint_handler(signal)

rclpy.init(args=None)
app_node = ROSNode()
t = threading.Thread(target=ros_spin, args=(app_node,))
t.start()
prev_sigint_handler = signal.signal(signal.SIGINT, sigint_handler)
# app.run(debug=True)

@app.route('/')
def hello():
    return render_template('index.html')

# data store - used instead of session because it is not working
data_store_locations = deque()
data_store_items = deque()

@app.route('/request', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def requestReceived():
    if request.method == 'POST':
        startLocation = request.json.get('start_location')
        endLocation = request.json.get('end_location')
        itemToSend = request.json.get('item')

        print(request.json)

        app_node.send_int_location(defineRobotLocation(startLocation))

        data = {
            'item': itemToSend
        }
        # if 'locations_list' not in session:
        #     session['locations_list'] = []  # Create a new list if it doesn't exist in the session
        # session['locations_list'].append(endLocation)  # Add the end location to the queue
        data_store_items.append(itemToSend)
        data_store_locations.append(endLocation)

        # add vue to the route and then route to the html file that has the progress bar
        print('Request received successfully')
        # print(session['locations_list'])
        return jsonify(data)

@app.route('/send', methods=['POST'])
@cross_origin(supports_credentials=True)
def returnButtonPushed():
    data = {'locationSent': False}
    location = ''
    # if 'location_list' in session:
    #     locations_list = session.get('locations_list', [])
    #     print(locations_list)
    #     location = locations_list[0] if locations_list else None   # Retrieve the location from the queue
    #     data['location'] = True
    #     # remove location from location list and send it to ROS
    #     locations_list.pop(0)
    #     sendDataToROS(location)
    #     print(f'Sent data succesfully {location}')
    if len(data_store_locations) > 0:
        location = data_store_locations.popleft()
        app_node.send_int_location(defineRobotLocation(location))
        data['location'] = True
        print(f'Sent data succesfully {location}')
    else:
        print('No locations available to send to robot')
    return jsonify(data)

# create an axios requests that sends location data to progress bar via a get request
# for now, 0 if request hasn't been queued, and 1 if request is been completed on the send side
@app.route('/location', methods=['GET'])
def sendLocationStatus():
    # location = ''
    location = 0
    if len(data_store_locations) == 0:
        # location = data_store_locations.popleft()
        location = 1
    # change robot location to string accordingly
    data = {'location': location}
    # make a call to robot to get it's current location
    return jsonify(data)

# write get item function
@app.route('/get-item', methods=['GET'])
def getItem():
    # grab item from the store if it exists, otherwise return nothing
    item = 'None' if (len(data_store_items) == 0) else data_store_items.pop()
    itemJson = {'item': item}
    return jsonify(itemJson)