 
class Common_Elements( object ):

   def __init__(self, app_files ):
       self.app_files = app_files

   def get_schedule_data( self, *args):
   
       sprinkler_ctrl           = self.app_files.load_file("sprinkler_ctrl.json")
       returnValue = {}
       for j in sprinkler_ctrl:
           data           = self.app_files.load_file(j["link"])           
           j["step_number"], j["steps"], j["controller_pins"] = self._generate_steps_(data)         
           returnValue[j["name"]] = j
       return returnValue


   def _generate_steps_( self, file_data):
       returnValue = []
       controller_pins = []
       if file_data["schedule"] != None:
           schedule = file_data["schedule"]        
           for i  in schedule:
               returnValue.append(i[0][2])
               temp = []
               for l in  i:
                   temp.append(  [ l[0], l[1][0] ] )
               controller_pins.append(temp)
  
  
       return len(returnValue), returnValue, controller_pins
