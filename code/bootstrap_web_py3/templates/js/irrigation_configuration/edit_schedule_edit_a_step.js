

var working_index;
var working_data;
function show_start_panel()
{
    $("#edit_panel").show();
    $("#edit_a_step").hide()
    $("#edit_steps").show()
    steps_load_controls(working_data)

}

function hide_edit_a_step_panel()
{
   $("#edit_a_step").hide()
}

function show_edit_a_step_panel()
{

  $("#edit_a_step").show()


}    


function back_button_step()
{
  
  show_start_panel();

}


function initialize_runtime()
{
         $("#step_run_timea").empty()
         for( var i = 0; i <= 180; i++ )
         {
             $("#step_run_timea").append($("<option></option>").val(i).html(i+'  minutes '));
	
         }

         
}


function initialize_edit_a_step()
{
   $( "#edit_a_step_back").bind("click",back_button_step )  

   $( "#step_choice" ).bind( "change", step_choice );
   $( "#step_run_timea").bind("change",run_time_function);
   initialize_runtime()
}


function show_edit_a_step( data, index  )
{
   working_index = index
   working_data  = data
   show_edit_a_step_panel()
   hide_edit_panel()

}



function run_time_function( event ,ui)
{
  var run_time

  run_time = $("#step_run_timea").val();
  working_data["steps"][working_index]  = run_time;

}

function step_choice(event, ui)
{
 var status
 var valve_index

 if( $("#step_choice").val() == "1" )
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
        set_status_bar("no valve selected")
     }
     
  }
  if( $("#step_choice").val() == "2" )
  {
     working_data["controller_pins"][working_index].push([]);
     working_valves    = working_data["controller_pins"][working_index]
     index = working_valves.length -1 
     load_valve( working_index, index, true )
     
     
  }
 
  if( $("#step_choice").val() == "3" )
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
        set_status_bar("no valve selected")
     }

     
  }
  if( $("#step_choice").val() == "4" )
  {
       
       show_edit_panel()
       generate_steps(working_data)
       $("#edit_a_step").hide()
     
  }
  if( $("#step_choice").val() == "5" )
  {
       show_start_panel();
     
  }
  $("#step_choice").val(0);
  
}





function edit_a_step_panel()
{
    ;

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
         
           
         $("#select-choice-2a").val(0);
         

         $("#define-schedule").hide()
         $("#edit_panel").hide();
         $("#edit_a_step").show()
         $("#edit_steps").hide()
         generate_valve(index, working_data)
         $("#step_run_timea").empty()
         for( var i = 0; i <= 180; i++ )
         {
             $("#step_run_timea").append($("<option></option>").val(i).html(i+'  minutes '));
	
         }

         

         $("#step_run_timea")[0].selectedIndex = working_data["steps"][working_index];
         

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
