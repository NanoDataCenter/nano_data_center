var field_keys = []
var data_length = 0
var draw_array = []
var x_start_index = 0
var x_start_range = 1.0 
var v_min
var v_max_ref 
var hh = {}


                  

function make_remote_changes()
{
   let select_index= $("#remote_index")[0].selectedIndex
   let temp = '/modbus_device_status/'+ select_index

   window.location.href = temp
}

function display_remotes()
{
    
    $("#remote_index").empty()
    for( i = 0; i < remotes.length; i++)
    {
        
        $("#remote_index").append($("<option></option>").val(i).html("Remote:  "+remotes[i]));
    } 

    $("#remote_index")[0].selectedIndex = remote_index;
    $("#remote_index").selectmenu("refresh")
}

function cancel_remotes()
{
     $( "#change_remotes" ).popup( "close" )
    
    
}

function make_refresh()
{
   let temp = '/irrigation_streaming_data/display_minute_irrigation/'+ref_field_index

   window.location.href = temp
}    
    
function change_field_index()
{
    
    $("#field_index").empty()
    for( i = 0; i < field_keys.length; i++)
    {
        
        $("#field_index").append($("<option></option>").val(i).html(field_keys[i]));
    } 

    $("#field_index")[0].selectedIndex = ref_field_index;
    $("#field_index").selectmenu("refresh")
}

function cancel_field_index()
{
     
     $( "#change_index" ).popup( "close" )
}

function save_field_index()
{
    ref_field_index = $("#field_index").val()
    v_min = Number.MAX_SAFE_INTEGER
    v_max = -Number.MAX_SAFE_INTEGER 
       
    display_data( ref_field_index )
    $( "#change_index" ).popup( "close" )
}
    
  


function prepare_data( )
{
  data_length = time_data.length
  let temp_keys = Object.keys(time_data[0])
  
  field_keys = []
  for( i =0; i< temp_keys.length; i++)
  {
     if( (temp_keys[i] != "time_stamp") &&(temp_keys[i] != "namespace"))
     {
       
        field_keys.push(temp_keys[i])
     }
  }
  field_keys.sort()
  draw_array = []
  time_data.reverse()
  
 
  v_min = Number.MAX_SAFE_INTEGER;
  v_max = -Number.MAX_SAFE_INTEGER;
  
  
}

function auto_scale()
{

  for( i = 0; i < draw_array.length;i++)
  {
     if( v_min > draw_array[i][1] )
     {
        v_min = draw_array[i][1] 
     }
     if( v_max < draw_array[i][1] )
     {
        v_max = draw_array[i][1] 
     }
   }
   if( v_min < 0 )
   {
      v_min = 1.25*v_min
   }
   else
   { 
      v_min = .75 *v_min
   }
   if( v_min == 0 )
   {
      v_min = -.5
   }
   if( v_max > 0 )
   {
      v_max = 1.25*v_max
   }
   else
   { 
      v_max = .75 *v_max
   }
   if( v_max == 0 )
   {
      v_max = .5
   }
}


function display_data( index )
{

  draw_array = []
  let field_key_ref = field_keys[index]
  $("#field_description").html("Current Selected Stream is:  "+field_key_ref )
  temp_x = Math.round(time_data.length *x_start_index)
  temp_x_range = Math.round(x_start_range *time_data.length)

  if( ( temp_x + temp_x_range ) >= time_data.length)
  {
     temp_x_range = time_data.length - temp_x
  } 
  
 
  for( let i = temp_x; i < temp_x+ temp_x_range; i++)
  {
    
     
     temp_data = [ new Date(time_data[i]["time_stamp"]),time_data[i][field_key_ref] ]
     draw_array.push(temp_data)
  }
   x_axis  = "time"
   y_axis  = field_key_ref
   if( v_min == Number.MAX_SAFE_INTEGER)
   {
      auto_scale()
   }

   hh.updateOptions( { 'file': draw_array,
                        'valueRange': [v_min, v_max ],
                        labels: [x_axis, y_axis]

                        } )
  
} 
 
$(document).ready(
 function()
 {  
   
    
   prepare_data( )
   
    
   limit_low = 0
   limit_high = 40
   x_axis  = "time"
   y_axis  = field_keys[0]
   hh = new Dygraph(document.getElementById("div_g"), draw_array,
                          {
                            width  : $(window).width()*.9,
                            height : $(window).height()*.65,
                            drawPoints: true,
                            showRoller: true,
                            valueRange: [limit_low, limit_high ],
                            labels: [x_axis, y_axis]
                          });
     
     
 
   display_data(ref_field_index)
   
  $("#make_remote_changes").bind("click", make_remote_changes);
  $("#cancel_remote_changes").bind("click",cancel_remotes);
  $("#change_remotes").on("popupafteropen", display_remotes );                      

   
  $("#cancel_index_changes").bind("click",cancel_field_index);
  $("#make_index_changes").bind("click", save_field_index );
  $("#change_index").on("popupafteropen", change_field_index );
                          


  $("#footer-button_2").bind("click",make_refresh)
  })
