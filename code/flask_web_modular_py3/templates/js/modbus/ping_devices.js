$(document).ready(
 function()
 {
     
     



     display_results = function(data)
     {
         
         $("#ping_result").val(data)

     } 
     function ping_device()
     {
       	
	    var json_object;
	    var json_string;
	    json_object = {}
        
        json_object["remote"]    = $("#remote_unit").val()


        $("#ping_result").val("")
        ajax_post_get('/ajax/ping_modbus_device', json_object, display_results, "Server Problem")
        
     }

   
     
     $("#ping_device").bind("click",ping_device )


  
   
  

  
 });
