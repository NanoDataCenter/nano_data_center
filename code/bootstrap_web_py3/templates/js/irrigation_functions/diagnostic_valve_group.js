

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

function populate_valves( index )
 {
     var pins;
     
     valves = valve_group_data[index].valves;
     $("#valve_select").empty()
     for( var i = 0; i <= valves.length; i++ )
     {
          $("#valve_select").append('<option value='+i+'>valve: '+(i+1)+' '+valves[i]+ ' </option>');	
	
     }
     $("#valve_select")[0].selectedIndex = 0;

}

function send_irrigation_event(event, ui) 
{
       var mode;
       var schedule_name;
       var step;
       var run_time;
       
       
       mode            = $("#op_mode").val()
       valve_group     =  $("#valve_group_select").val()
       valve           = $("#valve_select").val() 
       run_time        = $("#run_time").val()
       var valve_gp    = valve_group_data[valve_group]
       var io_list     = valve_gp["io"]
       io =              io_list[valve]
       var json_object = {}
       json_object["command"]     = $("#op_mode").val();
       json_object["controller"]  = io["controller"];
       json_object["pin"]         = io["pin"];
       json_object["run_time"]     = $("#run_time").val()
       
       ajax_post_confirmation("/ajax/mode_change", json_object,
                              "Do you want to make mode change", 
                                       "Changes Made", "Server Error" )
}   
   
function new_valve_group_event(event,ui)
{
   var index;
	  index = $("#valve_group_select")[0].selectedIndex;
   populate_valves( index );
}
      
function valve_group_success(  )
{

     

     $("#valve_group_select").empty()
     for( var i = 0; i < valve_group_data.length; i++ )
     {
        $("#valve_group_select").append('<option value='+i+'>'+valve_group_data[i].name+'</option>');	
     }
     $("#valve_group_select")[0].selectedIndex = 0;
 
     
     populate_valves( 0)
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
 

  
   
   
   $("#valve_group_select").bind("change", new_valve_group_event )
   
   $("#change_mode").bind("click",send_irrigation_event )
     
   $("#op_mode" ).bind( "change",mode_change );
   
   $("#schedule_div").hide()
   valve_group_success()
   
 

 }
)
