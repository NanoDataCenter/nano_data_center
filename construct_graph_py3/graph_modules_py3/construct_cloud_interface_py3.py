import json


class Construct_Cloud_Service(object):

   def __init__(self,bc,cd):
      self.bc = bc
      self.cd = cd
      
      bc.add_header_node("CLOUD_SERVICE_QUEUE")
      cd.construct_package("CLOUD_SERVICE_QUEUE_DATA")
      cd.add_job_queue("CLOUD_JOB_SERVER",2048,forward=False)
      cd.close_package_contruction()
      bc.end_header_node("CLOUD_SERVICE_QUEUE")

      bc.add_header_node("CLOUD_SERVICE_HOST_INTERFACE")
      
      bc.add_info_node( "HOST_INFORMATION","HOST_INFORMATION",properties={"host":"192.168.1.52" ,"port": 6379, "graph_db": 3, "key":"_UPLOAD_QUEUE_" } )
      bc.end_header_node("CLOUD_SERVICE_HOST_INTERFACE")
 