
//controller_pin_data = {} 

function  mode_change(event, ui) 
{  
        
   var temp_index
   temp_index = $("#op_mode")[0].selectedIndex;
	  $("#schedule_div").hide()
	  switch( temp_index)
	  {
	    
	    
	     case 1:  // Queue Schedule  Step Time
	           $("#schedule_div").show()
	           break;
   }
}

function populate_pins( index )
 {
     var pins;
     
     pins = controller_pin_data[index].pins;
  
     $("#select_pin").empty()
     
     for( var i = 1; i <= pins.length; i++ )
     {
          $("#select_pin").append('<option value='+i+'>pin: '+i+' '+pins[i-1]+ ' </option>');	
	
     }
     $("#select_pin")[0].selectedIndex = 0;

}

function send_irrigation_event(event, ui) 
{
       var mode;
       var schedule_name;
       var step;
       var run_time;
       
       
       mode            = $("#op_mode").val()
       controller      =  $("#controller_select").val()
       pin             = $("#select_pin").val() 
       run_time        = $("#run_time").val()
      
       var json_object = {}
       json_object["command"]     = $("#op_mode").val();
       json_object["controller"]  = $("#controller_select").val();
       json_object["pin"]         = $("#select_pin").val()
       json_object["run_time"]     = $("#run_time").val()
       ajax_post_confirmation("/ajax/mode_change", json_object,
                              "Do you want to make mode change", 
                                       "Changes Made", "Server Error" )
}   
   
function new_controller_event(event,ui)
{
   var index;
	  index = $("#controller_select")[0].selectedIndex;
   populate_pins( index );
}
      
function controller_pins_success(  )
{
  
     //controller_pin_data = JSON.parse(controller_pin_json)
     $("#controller_select").empty()
     
     for( var i = 0; i < controller_pin_data.length; i++ )
     {
        $("#controller_select").append('<option value='+controller_pin_data[i].name+'>'+controller_pin_data[i].name+'</option>');	
     }
     $("#controller_select")[0].selectedIndex = 0;
 
     
     populate_pins( 0)

}


$(document).ready(
 function()
 {
   
    $("#run_time").empty()
    for( var i = 5; i <= 60; i++ )
    {
          $("#run_time").append('<option value='+i+'>'+i+'  minutes </option>');	
	
    }
    $("#run_time")[0].selectedIndex = 0;
  

  
   
   
   $("#controller_select").bind("change", new_controller_event )
   
   $("#change_mode").bind("click",send_irrigation_event )
     
   $("#op_mode" ).bind( "change",mode_change );
   
   $("#schedule_div").hide()
   controller_pins_success()
 
 

 }
)
