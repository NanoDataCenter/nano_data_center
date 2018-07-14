var field_keys = []
var data_length = 0
var draw_array = []
var x_start_index = 0
var x_start_range = 1.0 
var v_min
var v_max_ref 
var hh = {}


    
  


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


function display_data(  )
{

  draw_array = []
  
 
  for( let i = 0; i < time_data.length; i++)
  {
    

     temp_data = [ new Date(time_data[i]["timestamp"]),time_data[i]["value"]*100 ]
     draw_array.push(temp_data)
  }
   x_axis  = "time"
 
 
   auto_scale()
   
 
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

   hh = new Dygraph(document.getElementById("div_g"), draw_array,
                          {
                            width  : $(window).width()*.9,
                            height : $(window).height()*.65,
                            drawPoints: true,
                            showRoller: true,
                            valueRange: [limit_low, limit_high ],
                            labels: [x_axis, y_axis]
                          });
     
    display_data()
 
 
  })
