#
#
# Setup of static pages
#
#
######################### Set up Static RoutesFiles ########################################

import os

class Load_Static_Files(object):
 
   def __init__( self,app,auth):
       self.app   = app
       self.auth  = auth

       a1 = auth.login_required( self.get_fav )
       app.add_url_rule('/favicon.ico',"get_fav",a1)
       a1 = auth.login_required( self.get_js )
       app.add_url_rule('/js/<path:filename>','get_js',a1)
       a1 = auth.login_required( self.get_css )
       app.add_url_rule('/css/<path:filename>','get_css',a1)
       a1 = auth.login_required( self.get_html )
       app.add_url_rule('/html/<path:filename>',"get_html",a1)



  
   def get_fav(self):
       return  self.app.send_static_file("favicon.ico")
       
       
   def get_js(self, filename):
       return self.app.send_static_file(os.path.join('js', filename))

 
   def get_css(self, filename):
       return self.app.send_static_file(os.path.join('css', filename))


   def get_html(self, filename):
       return self.app.send_static_file(os.path.join('html', filename))













