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




  
   
  

  
 });
