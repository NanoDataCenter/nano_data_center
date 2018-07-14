
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
   for( i = 0; i < schedules_pins[schedule_name][index].length;  i++)
   {
	     temp_string = temp_string + "   "+ schedules_pins[schedule_name][index][i];
         }
      return temp_string;
}


function schedule_success(data)
{
         
   schedules = []
   schedules_step = {}
   schedules_start_times = {}
   schedules_end_times = {}
   schedules_dow = {}
   schedules_pins = {}
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
   $("#manual_schedule").selectmenu();
	  $("#manual_schedule").selectmenu("refresh");
   set_step( 0 );
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
	   $("#manual_step").selectmenu();
	   $("#manual_step").selectmenu("refresh");
 
       
}
   
function bind_schedule_change()
{
      $( "#manual_schedule" ).bind( "change", function(event, ui) 
     {  
    
         set_step($("#manual_schedule")[0].selectedIndex )
     });
}

function bind_change_mode()
{
  $( "#change_mode" ).bind( "click", function(event, ui) 
  {
       var mode;
       var schedule_name;
       var step;
       var run_time;
       
       
       mode            = $("#op_mode").val()
       schedule_name   =  $("#manual_schedule").val()
       step            = $("#manual_step").val() 
       run_time        = $("#run_time").val()
      
     
       var json_object = {}
       json_object["command"] = mode;
       json_object["schedule_name"] = schedule_name;
       json_object["step"] = step;
       json_object["run_time"] = run_time;
       ajax_post_confirmation('/ajax/mode_change', json_object, 
                  "Do You Wish to Make Change","Changes Made", 
                  "Server Error" )
       
     });// change start time
 
}


function bind_op_mode_change()
{   

   $( "#op_mode" ).bind( "change", function(event, ui) 
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
	    
	         case 1:  // Queue Schedule  Step Time
              
	             $("#schedule_div").show()
              $("#manual_div").show()
              $("#run_div").show()
	             break;
	    
           case 2:  // open Master Valve
	             $("#schedule_div").hide()
              $("#manual_div").hide()
              $("#run_div").hide()
	             break;

           case 3: // Close Master Valve
	             $("#schedule_div").hide()
              $("#manual_div").hide()
              $("#run_div").hide()
	             break;

 
	     }

   });
}   

 
 


$(document).ready(
 function()
 {
 function schedule_setup()
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
      for( var i = 1; i <= 60; i++ )
      {
          $("#run_time").append('<option value='+i+'>'+i+'  minutes </option>');	
	
      }

      $("#run_time")[0].selectedIndex = 9;
      $("#run_time").selectmenu();
      $("#run_time").selectmenu("refresh")

     bind_schedule_change()
     bind_change_mode()
     bind_op_mode_change()
   
 
   
   
   

  
  
  ajax_get( '/ajax/schedule_data',
            '/ajax/schedule_data' +"   "+"Server Error Change not made",
            schedule_success )
   
   
         
       
     
  } // end of function
  
  schedule_setup()

  
 
 }
)





