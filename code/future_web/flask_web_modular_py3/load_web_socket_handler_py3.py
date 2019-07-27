#
#
# Code for test web socket
#
#
#
from flask_socketio import SocketIO
from flask_socketio import send, emit
from flask_socketio import Namespace


      



class MyCustomNamespace(Namespace):
    def on_connect(self):
        send("connection received")

           
           
    def on_disconnect(self):
        print("connection terminated")
        

    def on_ping_event(self, data):
        print("made it here")
        emit("ping_event",data)



class Load_Web_Socket_Handler(object):

   def __init__( self, app,auth, render_template ):
      
       self.app      = app
       self.render_template = render_template
       socketio = SocketIO(app)

       a1 = auth.login_required( self.get_socket_test_page )
       app.add_url_rule("/socket_test","socket_test",a1,methods=["GET"])
       socketio.on_namespace(MyCustomNamespace('/test'))
      

   def get_socket_test_page(self):
       return self.render_template("socket_io_test/socket_test",header_name="WEB SOCKET TEST")

       





