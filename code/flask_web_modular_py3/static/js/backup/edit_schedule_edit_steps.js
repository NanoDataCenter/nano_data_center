

function initialize_edit_panel()
{
   
   $( "#select-choice-1a" ).bind( "change", choice_1_function );

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
       if( $(item).is(":checked") == true )
       {
           return_value = [ true, i ]
       }
   }

   return return_value	              

}

function choice_1_function(event, ui)
{
 var status;
 if( $("#select-choice-1a").val() == "1" )
  {
     
     status = check_step_selection()
     if( status[0] == true )
     {
        show_editing_panel( status[1] )
     }
     else
     { 
         alert("no schedule selected")
     }
  }

     

  if( $("#select-choice-1a").val() == "2" )
  {

      working_data["controller_pins"].push([])
      working_data["steps"].push(0)
      generate_steps(working_data)
      show_editing_panel( working_data["steps"].length - 1  )
     
  }
  if( $("#select-choice-1a").val() == "3" )
  {
     status = check_step_selection()
     if( status[0] == true )
     {
        working_data["controller_pins"].splice(status[1],0,[])
        working_data["steps"].splice(status[1],0,0)
        generate_steps(working_data)
        show_editing_panel( status[1] )
     }
     else
     { 
         alert("no schedule selected")
     }

  }
  if( $("#select-choice-1a").val() == "4" )
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
         alert("no schedule selected")
     }

     
  }
  if( $("#select-choice-1a").val() == "5" )
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
         alert("no schedule selected")
     }

     
  }
 
  if( $("#select-choice-1a").val() == "6" )
  {
       show_start_panel();
     
  }
  $("#select-choice-1a").val(0);
  $("#select-choice-1a").selectmenu('refresh');
}



function show_edit_panel()
{
         
         $("#select-choice-1a").val(0);
         $("#select-choice-1a").selectmenu('refresh');
         $("#define-schedule").hide();
         $("#edit_panel").show();
         $("#start_time").hide();
         $("#edit_a_step").hide()
         $("#edit_steps").show()
         $("#edit_a_valve").hide()
         $("#master_save").show()

}    
