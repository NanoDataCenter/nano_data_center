$(document).ready(
 function()
 {
     
     

   $("#modbus_server").val( {{modbus_server_id|int  }});

   $("#modbus_server").bind('change',change_server)
 
   function change_server(event,ui)
   {
      current_page = window.location.href
      current_page = current_page.slice(0,-2)
  
      current_page = current_page+"/"+$("#modbus_server")[0].selectedIndex
      window.location.href = current_page
   }

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
