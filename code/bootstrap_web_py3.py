#
#
#  File: flask_web_py3.py
#
#
#
import os
import json
import redis


import flask
from flask import Flask
from flask import render_template,jsonify
from flask_httpauth import HTTPDigestAuth
from flask import request, session


class PI_Web_Server(object):

   def __init__(self , name, redis_site_data ):
       redis_handle_pw = redis.StrictRedis(redis_site_data["host"], 
                                           redis_site_data["port"], 
                                           db=redis_site_data["redis_password_db"], 
                                           decode_responses=True)

       startup_dict = redis_handle_pw.hgetall("web")
      
       app         = Flask(name) 
       auth = HTTPDigestAuth()
       auth.get_password( self.get_pw )
       startup_dict["DEBUG"]  = True
       self.startup_dict = startup_dict
       self.app = app
      
       app.template_folder       =   'flask_web_modular_py3/templates'
       app.static_folder         =   'flask_web_modular_py3/static'  
       app.config['SECRET_KEY']      = startup_dict["SECRET_KEY"]

       app.config["DEBUG"]           = True
       app.debug                     = True
       self.users                    = json.loads(startup_dict["users"])
  
       a1 = auth.login_required( self.get_index_page )
       app.add_url_rule('/index.html',"get_index_page",a1) 
       app.add_url_rule("/","get_slash_page",a1)

   def get_pw( self,username):
       
      
       if username in self.users:
           return self.users[username]
       return None
    
       
   def get_index_page (self):
       return "made it here"   

   def run_http( self):
       self.app.run(threaded=True , use_reloader=True, host='0.0.0.0',port=80)

   def run_https( self ):
       startup_dict          = self.startup_dict
      
       self.app.run(threaded=True , use_reloader=True, host='0.0.0.0',debug = True,
           port=int(startup_dict["PORT"]) ,ssl_context=(startup_dict["crt_file"], startup_dict["key_file"]))
       
 

   
   def get_pw( self,username):
       
      
       if username in self.users:
           return self.users[username]
       return None

 
       
if __name__ == "__main__":

   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
  
   redis_site_data = json.loads(data)


   pi_web_server = PI_Web_Server(__name__, redis_site_data  )
   pi_web_server.run_http()
   
   