
import json
from .Common_Elements_py3  import Common_Elements
class Composite_Elements(object):

   def __init__( self,history, render_template, redis_handle, app_files ):
      self.history = history
      self.render_template = render_template
      self.redis_handle = redis_handle
      common_element = Common_Elements(app_files)
      self.get_schedule_data = common_element.get_schedule_data
      
   def composite_statistics(self,schedule_index, field_index):
       
       schedule_data = self.get_schedule_data()
       schedule_list = sorted(list(schedule_data.keys()))
       schedule_name = schedule_list[schedule_index]
       
       step_number = schedule_data[schedule_name]["step_number"]
       step_list = []
       step_exists_list = []
       for i in range(0,step_number):
              step_list.append( "log_data:unified:"+schedule_name+":"+str(i+1))
              step_exists_list.append(self.redis_handle.exists(step_list[-1]))

       
       
       limit_list = []
       for i in range(0,step_number):
           if step_exists_list[i] == True:
              limit_list.append( "limit_data:unified:"+schedule_name+":"+str(i+1))
              if self.redis_handle.exists(limit_list[-1]) == False:  # limit doesnot exist
                   temp_name = step_list[i]                              # then use the latest value
                   temp_data = self.redis_handle.lindex(temp_name,0)
                   temp_name = limit_list[-1]
                   self.redis_handle.set(temp_name,temp_data)
                   
           else:
               limit_list.append(None)
               
       field_list = self.get_field_list(limit_list )
          
       data_object = []
       
       for i in range(0,len(step_list)):
           
           try:
               if step_exists_list[i]  :
                   temp_entry = {}
                   self.get_limit_data("limit_data:unified:"+schedule_name+":"+str(i+1))
                   self.get_schedule_list_data( self.history,"log_data:unified:"+schedule_name+":"+str(i+1))
                   temp_entry = {}
                   for j in field_list:
                       temp_field_element = {}
                       temp_field_element["limit"] = self.assemble_limit_data(j)
                       temp_field_element["data"]  = self.assemble_field_data(j)
                       temp_entry[j] = temp_field_element
           except:
               temp_entry = "None"
           data_object.append(temp_entry)

       return self.render_template("statistics/composite_statistics", 
                                     header_name = "Composite Irrigation",
                                     field_list = field_list,
                                     schedule_name = schedule_name, 
                                     schedule_list  = schedule_list,
                                     schedule_data  = schedule_data,
                                     step_number    = step_number,
                                     schedule_index = schedule_index,
                                     field_index       = field_index,
                                     data_object       = data_object   )
           
       return "SUCCESS"

   def get_field_list(self, limit_list ):
       for i in  range(0,len(limit_list)):
           if limit_list[i] != None :
               limit_data_json = self.redis_handle.get(limit_list[i])
               limit_data = json.loads(limit_data_json)
               fields = set(limit_data["fields"].keys())
               return sorted(fields)
       return [] 
       
   def get_limit_data(self, redis_key ):
       
           temp_data_json = self.redis_handle.get( redis_key )
        
           limit_data = json.loads(temp_data_json)
           self.limit_data = {}
           for key,item in limit_data["fields"].items():
               self.limit_data[key] = item["curve_fit"]["c"]
      
        
        
        
   def get_schedule_list_data(self, history, redis_key ):
       temp_data_list = self.redis_handle.lrange(redis_key,0,history)
       self.data_list = []
       for list_element_json in temp_data_list:
           list_element = json.loads(list_element_json)
           temp_element = {}
           for  key, item in list_element["fields"].items():
               temp_element[key] = item["curve_fit"]["c"]
           self.data_list.append(temp_element)


   def assemble_limit_data(self, field):
       return self.limit_data[field]

   def assemble_field_data(self, field):
       return_value = []
       for item in self.data_list:
           temp_element = item[field]
           return_value.append(temp_element)
       return return_value
       