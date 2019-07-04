import json


class Construct_Irrigation_Scheduling_Control(object):

   def __init__(self,bc,cd):
      self.bc = bc
      self.cd = cd
      bc.add_header_node("IRRIGIGATION_SCHEDULING_CONTROL")
      cd.construct_package("IRRIGIGATION_SCHEDULING_CONTROL_DATA")
      cd.add_hash("IRRIGATION_COMPLETION_DICTIONARY") 
      cd.add_hash("SYSTEM_COMPLETION_DICTIONARY")
      cd.add_hash("IRRIGATION_CONTROL")
      cd.add_hash("IRRIGATION_VALVE_TEST")
      cd.add_hash("IRRIGATION_TIME_HISTORY")
      cd.add_job_queue("IRRIGATION_VALVE_JOB_QUEUE",250)
      cd.add_job_queue("IRRIGATION_JOB_SCHEDULING",100,forward=False)
      cd.add_job_queue("IRRIGATION_PENDING",100)
      cd.add_job_queue("IRRIGATION_CURRENT",1)
    
      cd.add_redis_stream("IRRIGATION_PAST_ACTIONS",2000)
      cd.close_package_contruction()

      bc.add_info_node("IRRIGATION_CONTROL_FIELDS","IRRIGATION_CONTROL_FIELDS",properties={"access_keys":["RAIN_FLAG"]})
      bc.add_info_node("IRRIGATION_ETO_CONTROL","IRRIGATION_ETO_CONTROL",properties={"access_keys":"ETO_MANAGEMENT"})
      bc.add_info_node("MASTER_VALVES","MASTER_VALVES",properties={"MASTER_VALVES":[ {"remote":"satellite_1","pins":[43] } ]} )
      bc.add_info_node("CLEANING_VALVES","CLEANING_VALVES",properties= {"CLEANING_VALVES":[ {"remote":"satellite_1","pins":[44] } ]} )
      bc.add_info_node("MEASUREMENT_DEPTH","MEASUREMENT_DEPTH",properties = {"valve_depth":20} )
      bc.end_header_node("IRRIGIGATION_SCHEDULING_CONTROL")

