
var data_length = 0
var draw_array = []
var x_start_range = 0
var x_start_index = 0

var v_max_ref 
var hh = {}
var selected_field;
var selected_attribute;
var draw_data;

function draw_field(  )
{
    
    let maximium =   -Number.MAX_SAFE_INTEGER;
    bullet_initialize_canvas_a( valve_number,valve_list)
    
    for( i= 0; i< data_object.length; i++)
    {
        
        temp = data_object[i]
        if( temp != "None")
        {
           
           temp_data = temp['data']
           
           for( j = 0; j < temp_data.length; j++ )
           {
               if( temp_data[j] > maximium )
               {
                   maximium = temp_data[j]
               }
           }
       }
     }
   
    maximium = maximium/.75
   
    maximium = Math.ceil(maximium/5)*5;
    $("#legend_name").html("Valve Resistance For "+controller_name+"   Chart Max  "+maximium)
    
    for( let i= 0; i<valve_number; i++)
    {
       
        temp = data_object[i]
        if( temp != "None")
        {
           
           temp_data = temp['data']
           temp_limit = temp['limit']
           canvas_draw( i, temp_data , temp_limit, maximium ) 
        }
         
         
             
    }            

}


function make_refresh()
{
   let controller_id  =    $("#controller_select").val()
   
   
   let temp     = "/valve_resistance/"+controller_id
   
   window.location.href = temp
}    


function cancel_controller()
{
    
     
     $( "#change_controller" ).popup( "close" )
}


function populate_controller()
{
    
    $("#controller_select").empty()
    for( i = 0; i < controller_list.length; i++)
    {
        
        $("#controller_select").append($("<option></option>").val(i).html(controller_list[i]));
    } 
    
    $("#controller_select")[0].selectedIndex = controller_id
    $("#controller_select").selectmenu("refresh")
    
 }   

 

 
$(document).ready(
 function()
 {  
   
    
   draw_array = []

   bullet_initialize_canvas_a( valve_number,valve_list)
   
   
   draw_field()
   
                     
   
   $("#save_controller").bind("click",make_refresh);
   
   $("#cancel_controller").bind("click",cancel_controller);
   $("#change_controller").on("popupafteropen",populate_controller ); 


  
                           
   
  })

  