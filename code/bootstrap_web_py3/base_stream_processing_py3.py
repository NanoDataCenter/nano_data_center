

class Base_Stream_Processing(object):

   def format_data(self,stream_data,show_legend = False, title = "",title_x="",title_y="",ntick_x = 20,ntick_y=20):
      return_value = {}
      keys = list(stream_data[0]["data"].keys())
     
      for i in keys:
         new_key = i
         new_key = new_key.replace('%','')
         new_key = new_key.replace('/','')
         new_key = new_key.replace('-','_')
         return_value[new_key] = self.format_key(i,stream_data,show_legend,title,"Date",i,ntick_x,ntick_y)
     
      old_keys = keys
      
      keys = []
      for i in old_keys:
                  
         new_key = i
         new_key = new_key.replace('%','')
         new_key = new_key.replace('/','')
         new_key = new_key.replace('-','_')

         keys.append(new_key)
         
      stream_range = []

      if len(keys) > 0:
         for i in range(0,len(keys)):
            stream_range.append(i)
 
      return   keys,stream_range,return_value
      
   def format_data_variable_title(self,stream_data,show_legend = False,
                                  title = "",title_x="",title_y="",ntick_x = 20,ntick_y=20):
      return_value = {}
      keys = list(stream_data[-1]["data"].keys())
      
      for i in keys:
         new_key = i
         new_key = new_key.replace('%','')
         new_key = new_key.replace('/','')
        
         return_value[new_key] = self.format_key(i,stream_data,show_legend,title+i,"Date",i,ntick_x,ntick_y)
     
      old_keys = keys
      keys = []
      for i in old_keys:
                  
         new_key = i
         new_key = new_key.replace('%','')
         new_key = new_key.replace('/','')
         

         keys.append(new_key)
     
      stream_range = []
      for i in range(0,len(keys)):
         stream_range.append(i)

      return   keys,stream_range,return_value
      
   def format_key(self,key,stream_data,show_legend = False, title = "",title_x="",title_y="",ntick_x = 20,ntick_y=20):   
       data = {}
      
       x_axis = {
          "autorange":True,
          "showgrid":True,
          "zeroline":True,
          "ntick": ntick_x,
          "showline":True,
          "title":title_x,
          "mirror":"all"
          }
       y_axis = {
           "autorange":True,
           "showgrid":True,
           "zeroline":True,
           "ntick": ntick_y,
           "showline":True,
           "title":title_y,
           "mirror":"all"
      
            }      
       layout = {
           'title':title,
		   'showlegend': show_legend,
		   
            'xaxis':x_axis,
            'yaxis':y_axis,
	       };

       data = {}
         
       data["x"] = []
       data["y"] = []
        
      
      # assigning type
      
       data["type"] ="lines"+"markers"
       
       for i in stream_data:
           if key in i["data"]:
               
               ts = i["timestamp"]
               data["x"].append(ts)
               data["y"].append(i["data"][key])
      
       return {"data":data,"layout" : layout}     
      
       
   def format_data_specific_key(self,stream_data,show_legend = False, title = "",title_x="",title_y="",ntick_x = 20,ntick_y=20,specific_key = ""):
      return_value = {}
      keys = list(stream_data[0]["data"].keys())
     
      for i in keys:
         new_key = i
         new_key = new_key.replace('%','')
         new_key = new_key.replace('/','')
         new_key = new_key.replace('-','_')
         return_value[new_key] = self.format_specific_key(i,stream_data,show_legend,title+i,"Date",i,ntick_x,ntick_y,specific_key = specific_key)
     
      old_keys = keys
      keys = []
      for i in old_keys:
                  
         new_key = i
         new_key = new_key.replace('%','')
         new_key = new_key.replace('/','')
         new_key = new_key.replace('-','_')

         keys.append(new_key)
         
      stream_range = []
      for i in range(0,len(keys)):
         stream_range.append(i)

      return   keys,stream_range,return_value     
      
   def format_specific_key(self,key,stream_data,show_legend = False, title = "",title_x="",title_y="",ntick_x = 20,ntick_y=20,specific_key = ""):   
       data = {}
      
       x_axis = {
          "showgrid":True,
          "zeroline":True,
          "ntick": ntick_x,
          "showline":True,
          "title":title_x,
          "mirror":"all"
          }
       y_axis = {
           "showgrid":True,
           "zeroline":True,
           "ntick": ntick_y,
           "showline":True,
           "title":title_y,
           "mirror":"all"
      
            }      
       layout = {
           'title':title,
		   'showlegend': show_legend,
		   
            'xaxis':x_axis,
            'yaxis':y_axis,
	       };

       data = {}
         
       data["x"] = []
       data["y"] = []
        
      
      # assigning type
      
       data["type"] ="lines"+"markers"
       
       for i in stream_data:
           if key in i["data"]:
               
               ts = i["timestamp"]
               data["x"].append(ts)
               #print(i["data"])
               data["y"].append(i["data"][key][specific_key])
      
       return {"data":data,"layout" : layout}     
      
       