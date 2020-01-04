$(document).ready(
 function()
 {
     
     

   $("#modbus_server").val( {{modbus_server_id|int  }});
   $("#remote_unit").val( {{remote_unit_id|int  }});

   $("#modbus_server").bind('change',change_server)
 
   $("#remote_unit").bind('change',change_server) 
 
   function change_server(event,ui)
   {
      current_page = window.location.href
      current_page = current_page.slice(0,-4)
      
      current_page = current_page+"/"+$("#modbus_server")[0].selectedIndex+"/"+$("#remote_unit")[0].selectedIndex
      
      window.location.href = current_page
   }



  
 });
