from flask import Flask, render_template, request, session, jsonify
from flask_cors import CORS
#import rclpy
import queue
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)
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
    startLocation = request.json.get('start_location')
    endLocation = request.json.get('end_location')
    itemToSend = request.json.get('item')
    sendDataToROS(startLocation)
    print(f'Sent location data to ROS: {startLocation}')
    data = {
        'item': itemToSend
    }
    if 'locations_list' not in session:
        session['locations_list'] = list()  # Create a new queue if it doesn't exist in the session
    session['locations_list'].insert(0, endLocation)  # Add the end location to the queue
    # add vue to the route and then route to the html file that has the progress bar
    # connect this with a jinja template that is the same as the vue template
    print('Request received successfully')
    print(session['locations_list'])
    return jsonify(data)

# create an axios request that sends this information to the backend server
# worst case scenario, hard code it
@app.route('/send', methods=['POST'])
def returnButtonPushed():
    data = {'locationSent': False}
    location = 'None'
    if 'locations_list' in session:
        locations_list = session['locations_list']
        print(locations_list)
        if len(locations_list) > 0:
            location = locations_list[0]  # Retrieve the location from the queue
            data['location'] = True
            # remove location from location list and send it to ROS
            locations_list.pop(0)
            sendDataToROS(location)
        else:
            print('No locations available to send to robot')
    else:
        print('No locations available to send to robot')
    return jsonify(data)

# create an axios requests that sends data to progress bar via a get request
