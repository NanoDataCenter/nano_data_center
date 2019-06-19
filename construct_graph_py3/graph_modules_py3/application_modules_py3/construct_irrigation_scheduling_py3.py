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
      cd.add_job_queue("IRRIGATION_JOB_SCHEDULING",100,forward=False)
      cd.add_job_queue("IRRIGATION_PENDING",100)
      cd.add_job_queue("IRRIGATION_CURRENT",1)
      cd.add_stream("IRRIGATION_PAST_ACTIONS",2000)
      cd.close_package_contruction()
      bc.add_info_node("IRRIGATION_CONTROL_FIELDS","IRRIGATION_CONTROL_FIELDS",properties={"access_keys":["RAIN_FLAG"]})
      bc.end_header_node("IRRIGIGATION_SCHEDULING_CONTROL")

