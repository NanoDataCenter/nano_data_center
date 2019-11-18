function reset_irrigation_statistics(event, ui) 
{
       
       var json_object = {}

     
       
      
       ajax_post_confirmation('/ajax/reset_irrigation_logs', json_object, "Do You Want To Reset Irrigation Statistics", 
                                       "Changes Made", "Server Error" )
}


$(document).ready(
 function()
 {
   

   
 

  
   
 

     $( "#reset_irrigation_statistics" ).bind( "click",reset_irrigation_statistics )

    
   
   

  
 
}
)

