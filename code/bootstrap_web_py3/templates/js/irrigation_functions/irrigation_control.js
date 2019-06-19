function generate_description( index , schedule_name)
{
   var temp_string;
     
   temp_string = "step "+index+" controller/pins  --->";
   index = index -1;
   if( index >= schedules_pins[schedule_name].length)
   { 
       temp_string = "undefined"; 
       return temp_string; 
   }
   for( i = 0; i < schedules_pins[schedule_name][index].length;i++)
   {
	     temp_string = temp_string + "   "+ schedules_pins[schedule_name][index][i];
 	
   }
   return temp_string;
}


function set_step(index)
{
   var schedule_name;
	  var temp_string;
	  schedule_name = schedules[index];
   $("#manual_step").empty()
   for( var i = 1; i <= schedules_step[schedule_name].length; i++ )
	  {
	     temp_string = generate_description( i , schedule_name)
      $("#manual_step").append('<option value='+i+'>'+temp_string+'</option>');	
	
	  }

   $("#manual_step")[0].selectedIndex = 0;

 
       
       
       
}

function ajax_schedule_success()
{
         
   schedules = []
   schedules_step = {}
   schedules_start_times = {}
   schedules_end_times = {}
   schedules_dow = {}
   schedules_pins = {}
   data = JSON.parse(schedule_data_json);
   for (var i = 0; i < data.length; i++) 
   {   
	     schedules.push(data[i].name)
	     schedules_step[data[i].name]            = data[i].steps
      schedules_start_times[data[i].name]     = data[i].start_time
      schedules_end_times[data[i].name]       = data[i].end_time   
      schedules_dow[data[i].name]             = data[i].dow
      schedules_pins[data[i].name]            = data[i].controller_pins     
   }
   $("#manual_schedule").empty()
   for( var i = 0; i < schedules.length; i++ )
	  {
      $("#manual_schedule").append('<option value='+schedules[i]+'>'+schedules[i]+'</option>');	
	
	   }
       
   	 $("#manual_schedule")[0].selectedIndex = 0;

    set_step( 0 );
}

function op_mode_change(event, ui) 
{  
   var temp_index     
	  temp_index = $("#op_mode")[0].selectedIndex;	
	  switch( temp_index)
	  {
   
	     case  0:  // CLEAR
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
	         break;
	    
	     case 1:  // SKIP_STATION
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
          break;
	    
	     case 2: // QUEUE_SCHEDULE
	         $("#schedule_div").show()
          $("#manual_div").hide()
          $("#run_div").hide()
          break;

	     case 3:  // QUEUE_SCHEDULE_STEP
	         $("#schedule_div").show()
          $("#manual_div").show()
          $("#run_div").hide()
	         break;

      case 4: // QUEUE_SCHEDULE_STEP_TIME_A   
	         $("#schedule_div").show()
          $("#manual_div").show()
          $("#run_div").show()
	         break;


       case 5:  // OPEN_MASTER_VALVE
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
	         break;

       case 6: // CLOSE_MASTER_VALVE
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
	         break;

       case 7: // CLEAN_FILTER
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
	         break;

       case 8: // RESISTANCE_CHECK
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
	         break;

       case 9: // CHECK OFF
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
	         break;

       case 10: // SUSPEND
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
	         break;

       case 11: // RESUME
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
	         break;

       case 12: // RESET_SYSTEM Job Queue
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
	         break;

       case 13: // RESET_SYSTEM now
	         $("#schedule_div").hide()
          $("#manual_div").hide()
          $("#run_div").hide()
	         break;
  
   }
}

function  manual_schedule_change(event, ui) 
{  
    
   set_step($("#manual_schedule")[0].selectedIndex )
}
 
function schedule_irrigation_event(event, ui) 
{
       
       var json_object = {}

       json_object["command"]         = $("#op_mode").val()
       json_object["schedule_name"]   =  $("#manual_schedule").val()
       json_object["step"]        = $("#manual_step").val() 
       json_object["run_time"]        = $("#run_time").val()
      
       ajax_post_confirmation('/ajax/mode_change', json_object, "Do you want to make mode change", 
                                       "Changes Made", "Server Error" )
}

  


$(document).ready(
 function()
 {
   schedules_pins = {}
   schedules = []
   schedules_steps = {}
   schedules_start_times = {}
   schedules_end_times = {}
   schedules_dow = {}
   controller_pin_data = {}
   composite_limit_values = {}
     
     
            
   $("#schedule_div").hide()
   $("#manual_div").hide()
   $("#run_div").hide()

   $("#run_time").empty()
   for( var i = 1; i <= 120; i++ )
   {
       $("#run_time").append('<option value='+i+'>'+i+'  minutes </option>');	
	
   }

   $("#run_time")[0].selectedIndex = 9;

  
   $( "#op_mode" ).bind( "change",op_mode_change) 
   

   $( "#manual_schedule" ).bind( "change", manual_schedule_change )
 
 

     $( "#change_mode" ).bind( "click",schedule_irrigation_event )

    ajax_schedule_success()
   
   

  
 
}
)

