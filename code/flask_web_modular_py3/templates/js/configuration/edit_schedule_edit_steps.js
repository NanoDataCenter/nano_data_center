
function initialize_steps_control()
{
  
  $( "#steps_choice" ).bind( "change", choice_1_function );
}


function show_steps_panel()
{
   $("#edit_steps").show();
   $("#edit_a_step").hide();
   $("#edit_a_valve").hide();
}

function hide_steps_panel()
{
   $("#edit_steps").hide();
}

function steps_load_controls(temp_data)
{
   working_data = temp_data
   generate_steps(working_data)


}

function get_data_valve_data(data)
{
   
   
   data["controller_pins"] = working_data["controller_pins"]
   data["steps"]  = working_data["steps"]
   
}


function choice_1_function(event, ui)
{
 var status;

 if( $("#steps_choice").val() == "1" )
  {
     
     status = check_step_selection()
     if( status[0] == true )
     {
        show_editing_panel( status[1] )
     }
     else
     { 
         set_status_bar("no steps selected")
     }
  }

     

  if( $("#steps_choice").val() == "2" )
  {
      
      working_data["controller_pins"].push([])
      working_data["steps"].push(0)
      generate_steps(working_data)
      $("#current_valve").html("<h3>No Valves Defined</h3>")
      show_edit_a_step( working_data, working_data["steps"].length - 1  )
     
  }
  if( $("#steps_choice").val() == "3" )
  {
     status = check_step_selection()
     if( status[0] == true )
     { 
        
        working_data["controller_pins"].splice(status[1],0,[])
        working_data["steps"].splice(status[1],0,0)
        generate_steps(working_data)
        //alert(JSON.stringify(working_data))
        show_editing_panel( status[1] )
     }
     else
     { 
         set_status_bar("no steps selected")
     }

  }
  if( $("#steps_choice").val() == "4" )
  {
     status = check_step_selection()
     if( status[0] == true )
     {
     
        working_data["controller_pins"].splice(status[1]+1,0,[])
        working_data["steps"].slice(status[1]+1,0,0)
        generate_steps(working_data)
        show_editing_panel(status[1]+1)
     }
     else
     { 
         set_status_bar("no steps selected")
     }

     
  }
  if( $("#steps_choice").val() == "5" )
  {
     status = check_step_selection()
     if( status[0] == true )
     { 
        var result = confirm("Do you want to delete step ?");
        if( result == true )
        {
           working_data["controller_pins"].splice(status[1],1)
           working_data["steps"].splice(status[1],1)
           generate_steps(working_data)
        }
     }
     else
     { 
         set_status_bar("no steps selected")
     }

     
  }

  $("#steps_choice").val(0);
  $("#steps_choice").selectmenu('refresh');
}

function check_step_selection()
{  
   var update_flag;
   var item;
   var schedule;

   return_value = [false,null]
   
   for( i = 0; i <  working_data["steps"].length; i++ )
   {
  
       item = "#step-"+i+"a"
       //alert($(item).is(":checked"))
       if( $(item).is(":checked") == true )
       {
           return_value = [ true, i ]
       }
   }

   return return_value	              

}

function generate_steps(working_data)
{
  

   temp_steps = working_data["steps"]
   temp_pins  = working_data["controller_pins"]
   
   if( temp_steps.length == 0 )
   {
     $("#current_steps").html("<h3>No Steps Defined</h3>")

   }
   else
   {
      temp =  '<fieldset id="valve_list" data-role="controlgroup" >'
          
      
      for( i = 0; i < temp_steps.length; i++ )
      {
          temp1a = "step-"+i+"a"
          temp1 = "step-"+i
          concat_valves = ""
          for( j= 0; j< temp_pins[i].length; j++)
          {
             concat_valves = concat_valves + "( "+temp_pins[i][j][0] +","+temp_pins[i][j][1] +") "
          }
          temp = temp + '<input type="radio" name="edit_step_radio" id="'+temp1a+'"  value="'+temp1+'"/>'
          temp = temp+  '<label for="'+temp1+'">Step: '+(i+1)+'   Run Time: '+temp_steps[i]+"    Valves:    "+concat_valves +" </label> <BR>      "
      }
      temp = temp +'</fieldset>'

      $("#current_steps").html(temp)
 

   }

}

