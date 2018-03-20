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
       app.add_url_rule('/static/js/<path:filename>','get_js',a1)
       a1 = auth.login_required( self.get_js_library )
       app.add_url_rule('/static/js_library/<path:filename>','get_js_library',a1)
       a1 = auth.login_required( self.get_css )
       app.add_url_rule('/static/css/<path:filename>','get_css',a1)
       a1 = auth.login_required( self.get_images )
       app.add_url_rule('/static/images/<path:filename>','get_images',a1)
       a1 = auth.login_required( self.get_dynatree )
       app.add_url_rule('/static/dynatree/<path:filename>',"get_dynatree",a1)
       a1 = auth.login_required( self.get_themes )
       app.add_url_rule('/static/themes/<path:filename>','get_themes',a1)
       a1 = auth.login_required( self.get_html )
       app.add_url_rule('/static/html/<path:filename>',"get_html",a1)
       a1 = auth.login_required( self.get_app_images )
       app.add_url_rule('/static/app_images/<path:filename>',"get_app_images",a1)
       a1 = auth.login_required( self.get_data )
       app.add_url_rule('/static/data/<path:filename>',"get_data",a1)



  
   def get_fav(self):
       return self.app.send_static_file("favicon.ico")

   def get_js(self, filename):
       return self.app.send_static_file(os.path.join('js', filename))

   def get_js_library(self, filename):
       return self.app.send_static_file(os.path.join('js_library', filename))

   def get_css(self, filename):
       return self.app.send_static_file(os.path.join('css', filename))

   def get_images(self, filename):
       return self.app.send_static_file(os.path.join('images', filename))

   def get_dynatree(self, filename):
       return self.app.send_static_file(os.path.join('dynatree', filename))

   def get_themes(self, filename):
       return self.app.send_static_file(os.path.join('themes', filename))

   def get_html(self, filename):
       return self.app.send_static_file(os.path.join('html', filename))

   def get_app_images(self, filename):
       return self.app.send_static_file(os.path.join('app_images', filename))

   def get_data(self, filename):
       return self.app.send_static_file(os.path.join('data', filename))












