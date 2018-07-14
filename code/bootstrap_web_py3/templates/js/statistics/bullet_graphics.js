
var canvas_id_array = []
var window_width = 0
var context_array = []
var canvas_height = 7*14
var canvas_draw_pixel = 7
var text_boundary = 70
var text_indent_x = 10
var text_indent_y = canvas_height*.5
var major_grid_divisor = 10
var minor_grid_divisor = 20


/*
Public Functions
*/

function bullet_initialize_canvas_a( valve_number, valve_list )
{
 
    window_width  = $( window ).width()*.95
    for( let i = 0; i < valve_number; i++ )
    {
        _initialize_a_canvas_a(valve_list[i],window_width)
    }
  
    
}


function bullet_initialize_canvas( step_number)
{
    window_width  = $( window ).width()*.95
    for( let i = 0; i < step_number; i++ )
    {
        _initialize_a_canvas_(i,window_width)
    }
}
function canvas_draw( canvas_index, value_array , limit, max_value )
{
     let context = context_array[canvas_index]
    
    context.fillStyle = "Grey"; 
    context.fillRect(text_boundary,0,window_width,canvas_height );
    pixel_start = text_boundary
    pixel_range = window_width-pixel_start;
    pixel_step = pixel_range/max_value
    
    _draw_limit_( context, limit, "Black" , pixel_step )
    _draw_values_( context, value_array, "Orange" , pixel_step )
    _draw_minor_grid_( context,"Green")
    _draw_major_grid_( context,"Red")
        
} 


/*
Private Functions

*/


function _initialize_a_canvas_(step_index)
{
     
     let canvas_id = document.getElementById("canvas"+step_index)
     
     canvas_id_array.push(canvas_id)
     canvas_id.height = canvas_height+5
     canvas_id.width  = window_width    
     context =  canvas_id.getContext("2d"); 
     context_array.push(context)
     context.font="15px sans-serif";  
     context.fillStyle = "Grey";
     context.fillRect(text_boundary,0,window_width,canvas_height );
     context.fillStyle = "Black"
     context.textAlign = "left";
     context.fillText("Step "+(step_index+1),text_indent_x,canvas_height*.5);
                
}

function _initialize_a_canvas_a(valve_index)
{
     
     let canvas_id = document.getElementById("canvas"+valve_index)
     
     canvas_id_array.push(canvas_id)
     canvas_id.height = canvas_height+5
     canvas_id.width  = window_width    
     context =  canvas_id.getContext("2d"); 
     context_array.push(context)
     context.font="15px sans-serif";  
     context.fillStyle = "Grey";
     context.fillRect(text_boundary,0,window_width,canvas_height );
     context.fillStyle = "Black"
     context.textAlign = "left";
     context.fillText("valve "+(valve_index),text_indent_x,canvas_height*.5);
                
}

function _draw_major_grid_( context,fillStyle)
{
    context.fillStyle = fillStyle
    let size_base = (window_width - text_boundary)/major_grid_divisor
    for( let i = 1; i< major_grid_divisor ; i++)
    {
        let size_ref = text_boundary+(size_base*i)

        context.fillRect(size_ref,0,1,canvas_height)
    }
}


function _draw_minor_grid_( context,fillStyle)
{
    context.fillStyle = fillStyle
    let size_base = (window_width - text_boundary)/minor_grid_divisor
    for( let i = 1; i<minor_grid_divisor; i++)
    {
        let size_ref = text_boundary+(size_base*i)
        context.fillRect(size_ref,0,1,canvas_height)
    }
}

function _draw_limit_( context, value, fillStyle,  pixel_step )
{  
    
    context.fillStyle = fillStyle
    context.fillRect(text_boundary,0,text_boundary+value*pixel_step ,canvas_height)

}

function _draw_values_( context, values, fillStyle,  pixel_step )
{  
    
    context.fillStyle = fillStyle
    let y_value = canvas_height-canvas_draw_pixel+1
    for( let i =0; i< values.length; i++ )
    {
        
        context.fillRect(text_boundary,y_value,text_boundary+values[i]*pixel_step ,canvas_draw_pixel-4)
        y_value -= canvas_draw_pixel
    }
}        

