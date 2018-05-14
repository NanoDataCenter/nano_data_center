
var schedule_name = null;


function close_button(event, ui) 
{
          
          $("#define-schedule").show()   
          $("#edit_panel").hide();
}

function hide_edit_panel()
{
  $("#edit_panel").hide();

}

function show_edit_panel()
{
  $("#edit_panel").show();

}


function save_button(event, ui) 
{
     var i;
     var dow;
     var url;

     temp_data = {}
     temp_data["name"] = new_schedule
     temp_data["link"] = new_schedule+".json"
     get_data_time_page( temp_data)
     get_data_valve_data(temp_data)
     schedule_data[new_schedule] = temp_data
     confirmation_string = "Do you want to modify " + schedule_name
     
     make_change_update( new_schedule, schedule_data ,confirmation_string)
     location.reload()



 
}

function function_choice(event, ui)
{

  if( $("#function_choice").val() == "0" )
  {
      
       show_steps_panel()
       hide_time_panel()
  }
  else
  {
       hide_steps_panel()
       show_time_panel()
  }
 
}





function get_schedule_name()
{
    return schedule_name
}


function initialize_edit_functions()
{
  
  $( "#edit_panel_save" ).bind( "click", save_button );
  $( "#edit_panel_cancel" ).bind( "click", close_button );
  $( "#function_choice").bind("change", function_choice );
  initialize_time_control()
  initialize_steps_control()
  initialize_edit_a_step()
  initialize_edit_a_valve()

}


function load_controls( working_data )
{

  time_load_controls( working_data )
  steps_load_controls(working_data)

}


function edit_schedule_enable( sched_name)
{
    schedule_name = sched_name;
    $("#edit_panel_header").html( "Modify Setup For Schedule: "+sched_name);


    $("#edit_panel").show()
    $("#select-choice-0a").val(0)
    $("#select-choice-0a").selectmenu('refresh');
    show_steps_panel()
    hide_time_panel()
    hide_edit_a_step_panel()
    hide_edit_a_valve_panel()
    

}

