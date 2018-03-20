var working_data


function check_duplicate( new_schedule )
{   var i;
       
    for( i = 0; i < schedule_list.length; i++ )
    {
          if( schedule_list[i] == new_schedule )
          {
             return false;
           }
     }
     return true;
} 

function check_radio_selection()
{  
   var update_flag;
   var item;
   var schedule;

   return_value = [false,null]
   for( i = 0; i < schedule_list.length; i++ )
   {
       item = "#"+schedule_list[i]
       if( $(item).is(":checked") == true )
	      {
           return_value = [ true, schedule_list[i] ]
       }
   }
   return return_value	              

}


function edit_function(event, ui) 
{
   var temp;
   temp = check_radio_selection()
   if( temp[0] == true )
   {      
       new_schedule = temp[1]
       working_data  = JSON.parse(JSON.stringify( schedule_data[temp[1]]))
       load_controls( working_data )
       $("#define-schedule").hide()
       edit_schedule_enable(temp[1])
        
    }
    else
    {
       set_status_bar("no schedule selected")
    }
}



function load_new_schedule_data( schedule)
{
      working_data = {} 
      working_data["description"]      = ""
      working_data["step_number"]      = 0
      working_data["start_time"]       = [0, 0]
      working_data["link"]             = schedule+".json"
      working_data["end_time"]         = [0, 0]
      working_data["controller_pins"]  = []
      working_data["steps"]   = []
      working_data["dow"]     = [0, 0, 0, 0, 0, 0, 0] 
      working_data["name"]    = schedule
}

$(document).ready(
 function()
 {
    
      
      $( "#action_button" ).bind( "click", edit_function );
      initialize_edit_functions();


  //initialize_edit_panel();
  //initialize_start_panel();
  //initialize_edit_a_step_panel();
  //initialize_edit_a_valve_panel();
  hide_edit_panel()
  hide_edit_a_step_panel()
  hide_edit_a_valve_panel()

 }
)

