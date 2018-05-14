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


function add_function(event, ui) 
{
   new_schedule = $("#new_schedule" ).val()
   if( check_duplicate( new_schedule ) )
   {
          load_new_schedule_data( new_schedule )
          load_controls( working_data )
          $("#define-schedule").hide()
               

          edit_schedule_enable(new_schedule)
          
          
          
    }
    else
    {
       set_status_bar("duplicate schedule "+ $("#new_schedule" ).val())
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
    
      
      $( "#action_button" ).bind( "click", add_function );
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

