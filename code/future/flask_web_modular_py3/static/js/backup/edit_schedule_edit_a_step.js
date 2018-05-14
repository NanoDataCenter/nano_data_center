

var working_index;


function initialize_edit_a_step_panel()
{
  
   $( "#select-choice-2a" ).bind( "change", choice_2_function );
   $( "#step_run_timea").bind("change",run_time_function);
}

function run_time_function( event ,ui)
{
  var run_time

  run_time = $("#step_run_timea").val();
  working_data["steps"][working_index]  = run_time;

}

function choice_2_function(event, ui)
{
 var status
 var valve_index

 if( $("#select-choice-2a").val() == "1" )
  {
 
     status = find_selected_valve()
     if( status[0] == true )
     {
        $("#edit_a_step").hide()
        $("#edit_steps").hide()
        $("#start_time").hide()

        valve_index = status[1]
        load_valve( working_index, valve_index )
     }
     else
     {
        alert("no valve selected")
     }
     
  }
  if( $("#select-choice-2a").val() == "2" )
  {
     $("#edit_a_step").hide()
     $("#edit_steps").hide()
     $("#start_time").hide()
     working_data["controller_pins"][working_index].push([]);
     working_valves    = working_data["controller_pins"][working_index]
     index = working_valves.length -1 
     load_valve( working_index, index, true )
     
  }
 
  if( $("#select-choice-2a").val() == "3" )
  {
     status = find_selected_valve()
     if( status[0] == true )
     {
        index = status[1]
       
        var result = confirm("Do you want to delete selected valve:  " );
        if( result == true )
        {
            working_data["controller_pins"][working_index].splice(status[1],1)
            generate_valve(working_index, working_data)
        }
     }
     else
     {
        alert("no valve selected")
     }

     
  }
  if( $("#select-choice-2a").val() == "4" )
  {
       
       show_edit_panel()
       generate_steps(working_data)
       $("#edit_a_step").hide()
     
  }
  if( $("#select-choice-2a").val() == "5" )
  {
       show_start_panel();
     
  }
  $("#select-choice-2a").val(0);
  $("#select-choice-2a").selectmenu('refresh');
}





function edit_a_step_panel()
{
    alert("edit a step panel")

}


      
function show_editing_panel( index )
{
         var i;
         working_step_index = index
         $("#valve_time").empty()
         
         for( i =0; i<= 180; i++ )
         {
           $("#valve_time").append("<option value="+i+">"+i+"  min</option>")

         }
         $("#valve_time").selectmenu('refresh');
           
         $("#select-choice-2a").val(0);
         $("#select-choice-2a").selectmenu('refresh');

         $("#define-schedule").hide()
         $("#edit_panel").show();
         $("#edit_a_step").show()
         $("#edit_steps").hide()
         $("#start_time").hide()
         $("#edit_a_valve").hide()
         $("#master_save").hide() 
         generate_valve(index, working_data)
         $("#step_run_timea").empty()
         for( var i = 0; i <= 180; i++ )
         {
             $("#step_run_timea").append($("<option></option>").val(i).html(i+'  minutes '));
	
         }

         $("#step_run_timea").selectmenu();
         $("#step_run_timea").selectmenu("refresh");

         $("#step_run_timea")[0].selectedIndex = working_data["steps"][working_index];
         $("#step_run_timea").selectmenu();
         $("#step_run_timea").selectmenu("refresh");

}      

function find_selected_valve()
{
   var return_value
   var i
   var temp
   return_value = [false,null]
   working_valves    = working_data["controller_pins"][working_index]
   for( i = 0; i < working_valves.length; i++ )
   {
     temp = "#valve-"+i+"a"
      if( $(temp).is(":checked") == true )
       {
           return_value = [ true, i ]
       }

   }
   return return_value
}

function generate_valve(index, working_data)
{
   var temp
   var temp1
   var temp1a
   var i
   working_index     = index
   working_valves    = working_data["controller_pins"][index] 

   if( working_valves.length == 0 )
   {
     $("#current_valve").html("<h3>No Valves Defined</h3>")

   }
   else
   {
      temp =  '<fieldset id="valve_list" data-role="controlgroup" >'
          
      
      for( i = 0; i < working_valves.length; i++ )
      {
          temp1a = "valve-"+i+"a"
          temp1 = "valve-"+i
          temp = temp + '<input type="radio" name="edit_valve_radio" id="'+temp1a+'"  value="'+temp1+'"/>'
          temp = temp+  '<label for="'+temp1+'">Valve: '+(i+1)+'   Controller: '+working_valves[i][0] +"    Output:    "+working_valves[i][1]+" </label> <BR>      "
      }
      temp = temp +'</fieldset>'
 
      $("#current_valve").html(temp)
 

   }

}
