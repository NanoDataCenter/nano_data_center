import json


class Construct_Lacima_Cloud_Service(object):

   def __init__(self,bc,cd):
      self.bc = bc
      self.cd = cd
      
      bc.add_header_node("CLOUD_SERVICE_QUEUE")
      cd.construct_package("CLOUD_SERVICE_QUEUE_DATA")
      cd.add_job_queue("CLOUD_JOB_SERVER",2048,forward=False)
      cd.add_hash("CLOUD_SUB_EVENTS")
      cd.close_package_contruction()
      

      bc.add_header_node("CLOUD_SERVICE_HOST_INTERFACE")
      bc.add_info_node( "HOST_INFORMATION","HOST_INFORMATION",properties={"host":"192.168.1.41" ,"port": 6379, "key_data_base": 3, "key":"_UPLOAD_QUEUE_" ,"depth":1024} )
      bc.end_header_node("CLOUD_SERVICE_HOST_INTERFACE")
      bc.end_header_node("CLOUD_SERVICE_QUEUE")
 