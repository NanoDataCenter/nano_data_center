


class Cluster_Control(object):

   def __init__( self , cf):
      self.clusters       = {}
      
      self.chain_list = set([])
      self.cf             = cf
      

   def define_cluster( self, cluster_id, list_of_chains, initial_chain):

       set_chains = set(list_of_chains)
       
       self.validate_chain_list(list_of_chains)
      
       self.validate_cluster(cluster_id, False)
       self.clusters[cluster_id] = {}
       self.clusters[cluster_id]["initial_chain"] = initial_chain
       self.clusters[cluster_id]["chains"] = set(list_of_chains)
       self.clusters[cluster_id]["states"] = {}
       self.clusters[cluster_id]["current_state"] = None
       self.clusters[cluster_id]["suspension_state"] = False
       set_intersect = set_chains - self.chain_list
      
       if len( set_intersect ) != len(list_of_chains):
           raise ValueError("the following chains have already been defined ",(set_intersect))
       self.chain_list =  self.chain_list | set_chains
       self.clusters[cluster_id]["chains"] =  set_chains



   def define_state( self, cluster_id, state_id, list_of_chains):
       self.validate_chain_list(list_of_chains)
       set_chains = set(list_of_chains)
       self.validate_cluster(cluster_id, True)
       self.validate_state_id( cluster_id, state_id )       
       set_diff = set_chains - self.clusters[cluster_id]["chains"] 
       if len( set_diff ) != 0:
          raise ValueError("invalid states for cluster,  invalid states ",(cluster_id,state_id, set_diff))
       self.clusters[cluster_id]["states"][state_id] = set_chains

   def dump_chains( self ):
      return self.chain_list

   def dump_clusters( self):
      return self.clusters

   def validate_clusters_state(self, cf_handle ):
       return_value = []
       valid_chains = cf_handle.chain_map.keys()
       for i in self.clusters.keys():
           for j in self.clusters[i]["chains"]:
               if j not in valid_chains:
                   return_value.append(j)
               else:
                  position = cf_handle.chain_map[j]
                  cf_handle.chains[position]["auto_start"] = False
                  cf_handle.chains[position]["active"] = False
       if len( return_value ) != 0:
           raise ValueError("following chains are not valid",(return_value))


   def reset_cluster(self, cf_handle, chainObj, parameters, event):
       cluster_id = parameters[1]
       self.disable_cluster_states(  self.cf, self.clusters[cluster_id]["chains"])
       if  self.clusters[cluster_id]["initial_chain"] != None :
           self.reset_cluster_states( self.cf, [self.clusters[cluster_id]["initial_chain"]] )

   def suspend_cluster(self, cf_handle, chainObj, parameters, event):
       cluster_id = parameters[1]
       self.suspend_cluster_rt( cf_handle, cluster_id )

   def suspend_cluster_rt( self, cf_handle, cluster_id ):
       if self.clusters[cluster_id]["suspension_state"] == False:
          self.clusters[cluster_id]["suspension_state"] = True
          for i in self.clusters[cluster_id]["chains"]:
              position = cf_handle.chain_map[i]
              chain    = cf_handle.chains[position]
              if chain["active"] == True:
                   cf_handle.suspend_chain_code( [i])

   def resume_cluster(self, cf_handle, chainObj, parameters, event):
       cluster_id = parameters[1]
       self.resume_cluster_rt(cf_handle,cluster_id)

   def resume_cluster_rt( self, cf_handle,cluster_id ):
       if self.clusters[cluster_id]["suspension_state"] == True:
          self.clusters[cluster_id]["suspension_state"] = True
          for i in self.clusters[cluster_id]["chains"]:
              position = cf_handle.chain_map[i]
              chain    = cf_handle.chains[position]
              if chain["suspend"] == True:
                   cf_handle.resume_chain_code([i])
              
   def disable_cluster(self, cf_handle, chainObj, parameters, event):
       cluster_id = parameters[1]
       self.disable_cluster_rt( cf_handle,cluster_id )
   
   def disable_cluster_rt( self,cf_handle, cluster_id ):
       chains = self.clusters[cluster_id]["chains"]
       self.disable_cluster_states( cf_handle, chains)
               

   # parameter[1] is the cluster id
   # parameter[2] is the state id      
   def enable_cluster_reset(self, cf_handle, chainObj, parameters, event):
       cluster_id, state_id = self.validate_parameters( parameters)     
       self.enable_cluster_reset_rt( cf_handle, cluster_id, state_id)

   def enable_cluster_reset_rt( self, cf_handle, cluster_id, state_id ):
       enabled_states, disable_states = self.analyize_cluster_state( cluster_id, state_id)
       self.clusters[cluster_id]["current_state"] = state_id
       self.disable_cluster_states( cf_handle, disable_states)
       self.reset_cluster_states( cf_handle, enabled_states)
       return "DISABLE"

   def get_current_state(self,cluster_id):
      return self.clusters[cluster_id]["current_state"]
   '''
   Not usefull right now
   # parameter[1] is the cluster id
   # parameter[2] is the state id
   def enable_cluster_no_reset( self, cf_handle, chainObj, parameters, event ):
       cluster_id, state_id = self.validate_parameters( parameters)   
       self.enable_cluster_no_reset_rt(cf_handle, cluster_id, state_id)

   def enable_cluster_no_reset_rt(self,cf_handle, cluster_id, state_id)         
       enabled_states, disable_states = self.analyize_cluster_state( cluster_id, state_id)
       print("++++++",enabled_states, disable_states)
       current_enabled_states = self.determine_enabled_states( cf_handle, enabled_states)
       print("-----",enabled_states,disable_states)
       states_to_reset = enabled_states - current_enabled_states
       self.disable_cluster_states( cf_handle, disable_states)
       self.reset_cluster_states( cf_handle, states_to_reset)
       return "DISABLE"
   '''

   '''
   The next set of functions are internal worker functions
   '''
   def validate_parameters( self, parameters ):
       cluster_id = parameters[1]
       state_id   = parameters[2]
       
       self.validate_cluster( cluster_id, True)
       self.validate_state_id( cluster_id, state_id, True)
       
       return cluster_id,state_id


   def determine_enabled_states( self, cf, enabled_states):
       return_value = set()
       for i in enabled_states:          
           position = cf.chain_map[i]         
           if cf.chains[position]["active"]:
               return_value.add(i)
               
       
       return return_value

   def  disable_cluster_states( self, cf, states_to_reset):
        for j in states_to_reset:
            position = cf.chain_map[j]
            cf.chains[position]["auto_start"] = False  # allow reset before chain flow starts
            cf.disable_chain_base(j)
 
   def  reset_cluster_states( self, cf, states_to_reset):

        for j in states_to_reset:
            position = cf.chain_map[j]
            cf.chains[position]["auto_start"] = True  # allow reset before chain flow starts
            cf.enable_chain_base(j)

   def validate_cluster( self, cluster_id, condition):
       if condition == True:
           
           if cluster_id not in self.clusters:
               raise ValueError("cluster_id is not defined")
       else:
           if cluster_id  in self.clusters:
               raise ValueError("cluster_id is already defined")

       
   def validate_state_id( self, cluster_id, state_id , flag = False):
       if flag == False:
           
           if state_id  in self.clusters[cluster_id]["states"]:
               raise ValueError("duplicate definition for cluster %s and state_id %s ",(cluster_id,state_id))
       else:
           if state_id not in self.clusters[cluster_id]["states"]:
               raise ValueError("bad state definition  ",(cluster_id,state_id))


   def validate_chain_list( self, chain_list):
       if isinstance(chain_list,list):
          pass
       else:
            raise ValueError("list of chains should be a list instead of %s", type(chain_list))

   def analyize_cluster_state( self, cluster_id, state_id ):
       total_chains = self.clusters[cluster_id]["chains"]
       enabled_chains = self.clusters[cluster_id]["states"][state_id]
       disabled_chains = total_chains - enabled_chains
       return enabled_chains, disabled_chains

if __name__ == "__main__":

   from .chain_flow_py3    import CF_Base_Interpreter
   cf = CF_Base_Interpreter()
   cluster_control = Cluster_Control(cf)

   cf.define_chain("System_Startup",True)
   cf.insert.one_step(cluster_control.reset_cluster,"test_cluster")
   cf.insert.enable_chains(["Control_Chain"])
   cf.insert.terminate()

   cf.define_chain("Control_Chain",False)
   cf.insert.wait_event_count(count = 5) # 5 second delay
   cf.insert.one_step(cluster_control.enable_cluster_reset,"test_cluster","state_1")
   cf.insert.wait_event_count(count=5 ) # 5 second delay
   cf.insert.one_step(cluster_control.enable_cluster_reset,"test_cluster","state_2")
   cf.insert.wait_event_count(count=5 ) # 5 second delay
   cf.insert.one_step(cluster_control.enable_cluster_reset,"test_cluster","state_3")
   cf.insert.wait_event_count(count=5 ) # 5 second delay
   cf.insert.one_step(cluster_control.suspend_cluster,"test_cluster")
   cf.insert.wait_event_count(count=5 ) # 5 second delay
   cf.insert.one_step(cluster_control.resume_cluster,"test_cluster")
   cf.insert.wait_event_count(count=5 ) # 5 second delay
   cf.insert.one_step(cluster_control.disable_cluster,"test_cluster")

   cf.insert.reset()



   cf.define_chain("Initialize_Chain",False)
   cf.insert.log("Initial Chain Starting")
   cf.insert.log("Doing Setup Work")
   cf.insert.log("Initialize_Chain is terminating")
   cf.insert.terminate()

   cf.define_chain("State_1", False)
   cf.insert.log("State_1 is active")
   cf.insert.reset()

   cf.define_chain("State_2", False)
   cf.insert.log("State_2 is active")
   cf.insert.reset()

   cf.define_chain("State_3_Setup", False)
   cf.insert.log("State_3_Setup is active")
   cf.insert.enable_chains(["State_3A","State_3B"])
   cf.insert.wait_event_count( count = 5 ) # wait is to test the cluster no reset option
   cf.insert.terminate()

   cf.define_chain("State_3A", False)
   cf.insert.log("State_3A is active")
   cf.insert.reset()

   cf.define_chain("State_3B", False)
   cf.insert.log("State_3B is active")
   cf.insert.reset()



   test_list = ["Initialize_Chain","State_1","State_2","State_3_Setup","State_3A","State_3B"]
   cluster_control.define_cluster(cluster_id = "test_cluster", 
                               list_of_chains = test_list,
                               initial_chain = "Initialize_Chain" )
   
   cluster_control.define_state( "test_cluster", "state_1", ["State_1"])
   cluster_control.define_state( "test_cluster", "state_2", ["State_2"])
   cluster_control.define_state( "test_cluster", "state_3", ["State_3_Setup"])
   cluster_control.validate_clusters_state(cf)

   cf.execute()

