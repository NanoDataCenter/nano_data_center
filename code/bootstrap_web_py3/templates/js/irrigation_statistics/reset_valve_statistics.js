
function reset_valve_statistics(event, ui) 
{
       
       var json_object = {}

     
       
      
       ajax_post_confirmation('/ajax/reset_valve_logs', json_object, "Do You Want To Reset Valve Statistics", 
                                       "Changes Made", "Server Error" )
}


$(document).ready(
 function()
 {
   

   
 

  
   
 

     $( "#reset_valve_statistics" ).bind( "click",reset_valve_statistics )

    
   
   

  
 
}
)

