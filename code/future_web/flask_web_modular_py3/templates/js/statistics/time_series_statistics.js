 
 var draw_arraw
 var v_min
 var v_max
 
 
$(document).ready(
 function()
 {  
   
    
   draw_array = []

 
 
   limit_low = 0
   limit_high = 40
   x_axis  = "time"
   y_axis  = ""
   hh = new Dygraph(document.getElementById("div_g"), draw_array,
                          {
                            width  : $(window).width()*.9,
                            height : $(window).height()*.65,
                            drawPoints: true,
                            showRoller: true,
                            valueRange: [limit_low, limit_high ],
                            labels: [x_axis, y_axis]
                          });
   
    if( display_number_index <1 )
    {
        display_number_index = 1;
    }
    if( time_step_index => irrigation_data.length)
    {
        time_step_index = 0;
    }
    if( time_step_index +display_number_index > irrigation_data.length)
    {
        display_number_index = irrigation_data.length-1-time_step_index
    }
    field_name = field_list[ field_index]
   $("#field_description").html("Field: "+field_name+ "  Step Index: "+time_step_index +"  Display Number: "+display_number_index )
                        
   display_data( field_name, time_step_index, display_number_index )
    // schedule step                    
   $("#save_schedule_step").bind("click",display_new_schedule );
   $("#schedule_select").bind("change",schedule_change);
   $("#cancel_schedule_step").bind("click",cancel_schedule_step);
   $("#change_schedule_step").on("popupafteropen", populate_all ); 

   // field
   $("#save_field_index").bind("click", redraw_graph);
   $("#cancel_field_index").bind("click",cancel_field_index);
   $("#change_field_index").on("popupafteropen", populate_all );                      
                           
                          
      // step index
   $("#save_step_index").bind("click", redraw_graph);
   $("#cancel_step_index").bind("click",cancel_step_index);
   $("#change_step_index").on("popupafteropen", populate_all ); 
   
   // display number
   $("#save_display_number").bind("click", redraw_graph);
   $("#cancel_display_number").bind("click",cancel_display_number);
   $("#change_display_number").on("popupafteropen", populate_all );                      
                     
   
  })

  
  
 function redraw_graph()
{
   
   field_name     =               $("#field_select").val()
   time_step_index     =           parseInt(    $("#time_step_index").val())
   display_number_index    =     parseInt($("#display_number_select").val())
   
   $("#field_description").html("Field: "+field_name+ "  Step Index: "+time_step_index +"  Display Number: "+display_number_index )
   cancel_schedule_step()
   cancel_field_index()
   cancel_display_number()
   cancel_step_index()
   display_data( field_name, time_step_index, display_number_index )
}



function populate_all()
{
    populate_schedule_step()
    populate_fields_select()
    populate_step_index()
    populate_display_number()  
}

function populate_schedule_step()
{
    $("#schedule_select").empty()
    for( i = 0; i < schedule_list.length; i++)
    {
        
        $("#schedule_select").append($("<option></option>").val(i).html(schedule_list[i]));
    } 

    $("#schedule_select").val(schedule_id);
    $("#schedule_select").selectmenu("refresh")
    
    $("#step_select").empty()
    for( i = 0; i < step_number; i++)
    {
        console.log(i)
        $("#step_select").append($("<option></option>").val(i).html(i+1));
    } 

    $("#step_select")[0].selectedIndex = step;
    $("#step_select").selectmenu("refresh")
    
}

function populate_fields_select()
{
    
    $("#field_select").empty()
    for( let i = 0; i < field_list.length; i++)
    {
        
        $("#field_select").append($("<option></option>").val(field_list[i]).html(field_list[i]));
    } 
    
    $("#field_select").val(field_name)
    $("#field_select").selectmenu("refresh")
}

function populate_step_index()
{
    let length = irrigation_data.length
    
    $("#time_step_index").empty()
    for( let i = 0; i < length; i++)
    {
        
        $("#time_step_index").append($("<option></option>").val(i).html(i));
    } 

    $("#time_step_index").val(time_step_index)
    $("#time_step_index").selectmenu("refresh")
}

function populate_display_number()
{
    let length = irrigation_data.length
    let display_number = 14
    if( length < display_number )
    {
        display_number = length
    }
     $("#display_number_select").empty()
    for( let i = 1; i < display_number+1; i++)
    {
        
        $("#display_number_select").append($("<option></option>").val(i).html(i));
    } 
    
    
    $("#display_number_select").val(display_number_index)
    $("#display_number_select").selectmenu("refresh")
}  




function schedule_change()
{
     schedule_index = $("#schedule_select").val()

    let step_number = schedule_data[ schedule_list[schedule_index ] ]["step_number"]
    $("#step_select").empty()
    for( i = 0; i < step_number; i++)
    {
        
        $("#step_select").append($("<option></option>").val(i).html(i+1));
    } 

    $("#step_select")[0].selectedIndex = 0;
    $("#step_select").selectmenu("refresh")
}

function cancel_schedule_step()
{
    $( "#change_schedule_step" ).popup( "close" )
}

function  cancel_field_index()
{
    $( "#change_field_index" ).popup( "close" )
}

function  cancel_display_number()
{
    $( "#change_display_number" ).popup( "close" )
}

function  cancel_step_index()
{
    $( "#change_step_index" ).popup( "close" )
}


function display_new_schedule()
{
   let schedule_id  =         $("#schedule_select")[0].selectedIndex
   let step_id      =         $("#step_select").val()
   let field_id     =         $("#field_select")[0].selectedIndex
   let schedule_step     =    $("#time_step_index").val()
   let display_number    =    $("#display_number_select").val()
   let temp     = "/time_series_statistics/"+schedule_id+"/"+step_id+"/"+field_id+"/"+schedule_step+"/"+display_number
   
   window.location.href = temp
} 




function display_data( field_name, step_index, display_number )
{
     
    if( irrigation_data.length == 0 )
    {
        return;  // no data canot draw
    }
    if( step_index >= (irrigation_data.length -display_number))
    {
        step_index = irrigation_data.length-display_number -1 
        
    }
    if( step_index < 0)
    {
        step_index = 0;
    }
    
    if( ( step_index + display_number) > irrigation_data.length )
    {
        display_number = irrigation_data.length - step_index-1;
    }
    
    max_data_length = find_max_data_length(field_name,step_index, display_number )
    
    labels = assemble_labels(step_index, display_number)
    
    draw_array = assemble_data( max_data_length, field_name, step_index, display_number)
    scale = auto_scale()
    
    hh.updateOptions( { 'file': draw_array,
                     'valueRange': scale,
                        'labels': labels
     
                        } )    
    
    
}


function find_max_data_length(field_name ,step_index, display_number )
{
    return_value = limit_data[field_name].length
   
    for( let i = step_index ; i<=step_index+display_number; i++)
    {
       
        temp_length = irrigation_data[i][field_name].length
        if( temp_length > return_value )
        {
            return_value = temp_length;
        }
    }
    
    return return_value
}

function assemble_labels( step_index, display_number )
{
    labels = []
    labels.push("minutes")
    labels.push("baseline")

    for( i = step_index; i < step_index + display_number; i++)
    {   
        labels.push(i)
    }
    
    return labels
}    
    
function assemble_data(max_time, field_name, step_index, display_number)
{
    
    draw_array = []
    
    
    for( i = 0; i < max_time; i++ )
    {
        temp_element = []
        temp_element.push(i)
        temp_element.push(data_filter(limit_data[field_name],i))
        for( j = step_index; j < step_index + display_number;j++)
        {
            temp_element.push(data_filter(irrigation_data[j][field_name],i))
        }
        
        draw_array.push(temp_element)
    }
    
    return draw_array
}

function data_filter( element, index )
{
    if(element.length > index )
    {
        return_value = element[index]
    }
    else
    {
        return_value = 0
    }
    
    return return_value
}

function auto_scale()
{
   v_min = Number.MAX_SAFE_INTEGER;
   v_max = -Number.MAX_SAFE_INTEGER;

  for( i = 0; i < draw_array.length;i++)
  {
      for( j = 1; j < draw_array[i].length; j++)
      {
         if( v_min > draw_array[i][j] )
         {
        
            v_min = draw_array[i][j] 
         }
         if( v_max < draw_array[i][j] )
         {
          v_max = draw_array[i][j] 
         }
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
   
   return_value = [ v_min,v_max]
   return return_value
 

}

  