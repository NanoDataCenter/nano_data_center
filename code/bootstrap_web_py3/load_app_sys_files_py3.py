
import os
import json

class Load_App_Sys_Files(object):

   def __init__( self, app, auth, request, app_files, sys_files ):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.app_files = app_files
       self.sys_files = sys_files

       a1 = auth.login_required( self.get_system_file )
       app.add_url_rule("/ajax/get_system_file/<path:file_name>","get_system_file",a1)
       a1 = auth.login_required( self.get_app_file )
       app.add_url_rule("/ajax/get_app_file/<path:file_name>","get_app_file",a1)
       a1 = auth.login_required( self.save_app_file )
       app.add_url_rule("/ajax/save_app_file/<path:file_name>","save_app_file",a1,methods=["POST"])
       a1 = auth.login_required( self.save_sys_file )
       app.add_url_rule("/ajax/save_sys_file/<path:file_name>","save_sys_file",a1,methods=["POST"])
               


   def get_system_file(self, file_name):   
       data = self.sys_files.load_file(file_name)
      
       return json.dumps(data)

   def get_app_file(self,file_name):
       return json.dumps(self.app_files.load_file(file_name))
               
   def save_app_file(self,file_name):
       json_object = self.request.json
       self.app_files.save_file(file_name, json_object );
       return json.dumps('SUCCESS')

   def save_sys_file(self,file_name):
       json_object = self.request.json
       self.sys_files.save_file(file_name, json_object );
       return json.dumps('SUCCESS') 
       
       
       