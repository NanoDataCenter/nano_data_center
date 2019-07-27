var field_keys = []
var data_length = 0
var draw_array = []
var x_start_index = 0
var x_start_range = 1.0 
var v_min
var v_max_ref 
var hh = {}
var False = false
var True  = true

function make_refresh()
{
   let  selected_index = $("#field_index").val()
   let temp = '/control/display_past_actions/'+selected_index

   window.location.href = temp
}    
    
function change_field_index()
{
    
    $("#field_index").empty()
    for( i = 0; i < field_keys.length; i++)
    {
        
        $("#field_index").append($("<option></option>").val(field_keys[i]).html(field_keys[i]));
    } 

    $("#field_index").val(ref_field_index)
    $("#field_index").selectmenu("refresh")
}

function cancel_field_index()
{
     
     $( "#change_index" ).popup( "close" )
}

   
  


function prepare_data( )
{
  data_length = time_data.length
 
  
  field_keys = Object.keys(events)
  field_keys.sort()
 
  for( i= 0; i < data_length; i++ )
  {
     let status = time_data[i].status.toUpperCase();
     if( status == "GREEN")
     {    
        $("#radio-choice-v"+i).next('label').children('span').css('background-color', 'green');
        $("#radio-choice-v"+i).next('label').children('span').css('color', 'yellow');
        $("#radio-choice-v"+i).checkboxradio("refresh");    
     }
     else if( status == "YELLOW")
     {    
        $("#radio-choice-v"+i).next('label').children('span').css('background-color', 'yellow');
        $("#radio-choice-v"+i).next('label').children('span').css('color', 'black');
        $("#radio-choice-v"+i).checkboxradio("refresh");    
     }
     else if( status == "RED")
     {    
        $("#radio-choice-v"+i).next('label').children('span').css('background-color', 'red');
        $("#radio-choice-v"+i).next('label').children('span').css('color', 'white');
        $("#radio-choice-v"+i).checkboxradio("refresh");    
     }
     else
     {
         alert("this should not happen")
     }

      
  }
   
 

}


function display_data( index )
{

   
  
} 

function radio_select()
{
  
    
    $("#description").html( JSON.stringify(time_data[this.value].data) )
}
 
$(document).ready(
 function()
 {  
   
   
   prepare_data( )

     
 
   display_data(ref_field_index)
   
  $("#cancel_index_changes").bind("click",cancel_field_index);
  $("#make_index_changes").bind("click", make_refresh );
  $("#change_index").on("popupafteropen", change_field_index );
  //$('input[type=radio][name=radio-choice]').change(radio_select); 

  
  })
