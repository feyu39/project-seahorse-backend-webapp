from flask import Flask, render_template, request, session, jsonify
from flask_cors import CORS, cross_origin
from flask_session import Session
#import rclpy
import secrets

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax'
)
app.secret_key = secrets.token_hex(32)

# enable CORS
Session(app)
CORS(app)

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

def defineRobotLocation(location):
    robotLocation = 0
    if "V&V" in location:
        robotLocation = 1
    elif 'Demo' in location:
        robotLocation = 2
    elif 'Cafeteria' in location:
        robotLocation = 3
    return robotLocation

def sendDataToROS(location):
    # label based on recieve

    # int or xyz or string, 
    # from the payload get data
    # # ROS Communication
    # rclpy.init()
    # node = ROSNode()
    # node.publish_message(robotLocation)
    # rclpy.shutdown()
    print("Data sent to ROS\n")
    return

@app.route('/request', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def requestReceived():
    # if request.method == 'OPTIONS':
    #     # Preflight request. Reply successfully:
    #     resp = app.make_default_options_response()

    #     # Allow CORS on this route:
    #     headers = resp.headers
    #     headers['Access-Control-Allow-Origin'] = '*'
    #     headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    #     headers['Access-Control-Allow-Methods'] = 'GET, POST'

    #     return resp
    if request.method == 'POST':
        startLocation = request.json.get('start_location')
        endLocation = request.json.get('end_location')
        itemToSend = request.json.get('item')
        sendDataToROS(startLocation)
        print(f'Sent location data to ROS: {startLocation}')
        data = {
            'item': itemToSend
        }
        if 'locations_list' not in session:
            session['locations_list'] = []  # Create a new list if it doesn't exist in the session
        session['locations_list'].append(endLocation)  # Add the end location to the queue
        # add vue to the route and then route to the html file that has the progress bar
        # connect this with a jinja template that is the same as the vue template
        print('Request received successfully')
        print(session['locations_list'])
        return jsonify(data)

# create an axios request that sends this information to the backend server
# worst case scenario, hard code it
@app.route('/send', methods=['POST'])
@cross_origin(supports_credentials=True)
def returnButtonPushed():
    print(session)
    data = {'locationSent': False}
    location = 'None'
    if 'location_list' in session:
        locations_list = session.get('locations_list', [])
        print(locations_list)
        location = locations_list[0] if locations_list else None   # Retrieve the location from the queue
        data['location'] = True
        # remove location from location list and send it to ROS
        locations_list.pop(0)
        sendDataToROS(location)
        print(f'Sent data succesfully {location}')
        session.modified = False
    else:
        print('No locations available to send to robot')
    print(session)
    return jsonify(data)

# create an axios requests that sends data to progress bar via a get request
# best way is to grab from the robot, for now it is hardcoded
@app.route('/location', methods=['GET'])
def sendLocationStatus():
    data = {'location': 1}
    # make a call to robot to get it's current location
    return jsonify(data)