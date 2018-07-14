

     



 
     
function make_refresh()
{
   let schedule_id  =    $("#schedule_select").val()
   
   
   let temp     = "/configure_irrigation_limits/"+schedule_id
   
   window.location.href = temp
}    


function cancel_schedule()
{
    
     
     $( "#change_schedule_step" ).popup( "close" )
}


function populate_schedule()
{
    
    $("#schedule_select").empty()
    for( i = 0; i < schedule_list.length; i++)
    {
        
        $("#schedule_select").append($("<option></option>").val(i).html(schedule_list[i]));
    } 
    
    $("#schedule_select")[0].selectedIndex = schedule_id
    $("#schedule_select").selectmenu("refresh")
    
 }   

      
function save_data()
{
       var temp;
       var json_object;
       var json_string;
       var i;
            
	
       temp = []
       json_object  = {}
       json_object["schedule_name"] = schedule_name
       json_object["step_list"] = []
       for( i = 0; i < step_number; i++ )
       {
	  temp = $("#id"+i).is(':checked')
	  json_object["step_list"].push(temp)
	       
       }
       
       
        ajax_post_confirmation("/ajax/update_irrigation_limits", json_object, "Do you want to update values", 
                                       "Changes Made", "Server Error changes not made" )
       for( i = 0; i< step_number;i++)
       {
	       $("#id"+i).attr("checked",false).checkboxradio("refresh")
       }       
}
     	
     
  
$(document).ready(
 function()
 {  
  
   
   $("#footer-button_2").bind("click",save_data);
   $("#save_schedule_step").bind("click",make_refresh);
   $("#cancel_schedule_step").bind("click",cancel_schedule);
   $("#change_schedule_step").on("popupafteropen", populate_schedule ); 

 }


)
