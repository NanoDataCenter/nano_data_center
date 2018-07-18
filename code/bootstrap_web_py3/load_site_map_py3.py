import os
import json

class Load_Site_Data(object):

   def __init__( self, app, auth,render_template ):
       self.app      = app
       self.auth     = auth
       self.render_template = render_template

       a1 = auth.login_required( self.get_site_data )
       app.add_url_rule('/site_map/<int:map_type>',"site_map",a1,methods=["GET"])


   def get_site_data(self,map_type):
       template = "site_map/site_map_"+str(map_type)
       
       return self.render_template(template)
      