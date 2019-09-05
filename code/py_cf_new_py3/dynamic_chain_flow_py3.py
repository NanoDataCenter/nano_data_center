


class DYNAMIC_CHAIN_FLOW(object):

   def __init__(self):
        self.valid_return_codes = {}
        self.valid_return_codes["CONTINUE"] = 1
        self.valid_return_codes["HALT"] = 1
        self.valid_return_codes["RESET"] = 1
        self.valid_return_codes["DISABLE"] = 1
        self.valid_return_codes["TERMINATE"] = 1
        
        
        
   def dynamic_chain(self,chain_objects):
       self.chain_list = []
       for i in chain_objects:
          link_object ={}
          link_object["ACTIVE"] = True
          link_object["INIT"]   = False
          link_object["ELEMENT"] = i
          self.chain_list.append(link_object)

   def reset_chain(self):  
       chain_object = self.chain_list   
       self.chain_list = []
       for i in chain_objects:
          link_object ={}
          link_object["ACTIVE"] = True
          link_object["INIT"]   = False
          link_object["ELEMENT"] = i
          self.chain_list.append(link_object)         
          
   def execute_chain(self,event):
       for i in self.chain_list:
         if i["ACTIVE"] != True:
            continue
         if i["INIT"] == False
            i["ELEMENT"]("INIT",None)
         return_value = i["ELEMENT"](event["name"],event["data"])
         assert returnCode in self.valid_return_codes, "bad returnCode " + return_value
            
         if return_value == "DISABLE":
            i["ACTIVE"]  = False
            continue
         elif return_value == "HALT":
            return return_code

         elif return_value == "TERMINATE"           
            break
         elif return_value == "RESET""
            self.reset_chain()
       return return_value        
           
       
         
         