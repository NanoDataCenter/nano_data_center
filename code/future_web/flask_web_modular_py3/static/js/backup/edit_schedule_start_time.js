

function choice_0_function(event, ui)
{

  if( $("#select-choice-0a").val() == "1" )
  {
      
      show_edit_panel()
  }
 
}




function initialize_start_panel()
{
   
   $( "#select-choice-0a" ).bind( "change", choice_0_function );
}


function show_start_panel()
{
    $("#select-choice-0a").val(0)
    $("#select-choice-0a").selectmenu('refresh');
    $("#define-schedule").hide();
    $("#edit_panel").show();
    $("#start_time").show();
    $("#edit_a_step").hide()
    $("#edit_steps").hide()
    $("#edit_a_valve").hide()
    $("#master_save").show() 
    
}

