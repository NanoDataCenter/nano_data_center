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
  	    
	     case 0: // MARK_SCHEDULE
	         $("#schedule_div").show()
             $("#manual_div").hide()
           
          break;

	     case 1:  // QUEUE_SCHEDULE_STEP
	         $("#schedule_div").show()
             $("#manual_div").show()
           
	      break;

      case 2: // Mark All Valves 
	     $("#schedule_div").hide()
          $("#manual_div").hide()
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

     
       json_object["valve_list"]        = generate_valve_list()
      
       ajax_post_confirmation('/ajax/mark_irrigation_data', json_object, "Do You Want To Mark Valves", 
                                       "Changes Made", "Server Error" )
}

function generate_valve_list()
{
      var return_value = []
      var temp_index = $("#op_mode")[0].selectedIndex;
      var valve_dict = {}      
	  switch( temp_index)
	  {
  	      case 0:
               schedule_selection = $("#manual_schedule").val()
               
               for(i = 0; i< schedules_pins[schedule_selection].length;i++)
               {
                   return_value.push(format_step(valve_dict ,schedules_pins[schedule_selection][i]))
                   
               }
               
               break;
          case 1:
               schedule_selection = $("#manual_schedule").val()
               step_selection = $("#manual_step").val()
               return_value.push(format_step(valve_dict,schedules_pins[schedule_selection][step_selection-1]))
               break;
          case 2:
                return_value =JSON.parse(valve_keys_json)          
                break;
      }
      return return_value
}  

function format_step(valve_dict,step_entry)
{
   return_value = ""
   for( j = 0;j<step_entry.length;j++)
   {
       if( return_value == "")
       {
        return_value = format_entry(valve_dict,step_entry[j])
       }
       else
       {
           return_value = return_value+"/"+format_entry(valve_dict,step_entry[j])
       }
   }
   return return_value
    
    
}

function format_entry(valve_dict,entry)
{
    return entry[0]+":"+entry[1]
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
     
     
            
   $("#schedule_div").show()
   $("#manual_div").hide()
   

   
 

  
   $( "#op_mode" ).bind( "change",op_mode_change) 
   

   $( "#manual_schedule" ).bind( "change", manual_schedule_change )
 
 

     $( "#change_mode" ).bind( "click",schedule_irrigation_event )

    ajax_schedule_success()
   
   

  
 
}
)

