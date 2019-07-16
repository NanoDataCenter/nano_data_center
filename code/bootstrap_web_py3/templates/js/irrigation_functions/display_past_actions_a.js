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
 
  
  
 
  for( i= 0; i < data_length; i++ )
  {
     let status = time_data[i]["data"].level.toUpperCase();
     
     if( status == "GREEN")
     {    
        $("#entry_"+i).next('label').children('span').css('background-color', 'green');
        $("#entry_"+i).next('label').children('span').css('color', 'yellow');
        
     }
     else if( status == "YELLOW")
     {    
        $("#entry_"+i).next('label').children('span').css('background-color', 'yellow');
        $("#entry_"+i).next('label').children('span').css('color', 'black');
      
     }
     else if( status == "RED")
     {   
        
        $("#entry_"+i).css('background-color', 'red');
        $("#entry_"+i).css('color', 'white');
          
     }
     else
     {
         alert("this should not happen")
     }

      
  }
   
 

}


function display_data(  )
{

   
  
} 

function radio_select()
{
  
    
    $("#description").html( JSON.stringify(time_data[this.value].data) )
}
 
$(document).ready(
 function()
 {  
   
   
   //prepare_data( )

     
 
   //display_data()
   
   

  
  })
