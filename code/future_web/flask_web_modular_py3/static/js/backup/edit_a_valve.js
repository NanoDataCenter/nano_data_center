var step_index
var valve_index
var current_valve
var step_valves

var controller_labels = {}
var controller_list   = []
var controller_values = {}

function valve_panel_controller_select()
{

   var index = $("#valve_controllera").val()
   refresh_valve( index, 0)

}

function valve_panel_valve_select()
{
;
}

function valve_panel_save()
{
   var temp = []

   temp = [$("#valve_controllera").val(), $("#valve_valvea").val()]
 
   var index = $("#valve_valvea")[0].selectedIndex;
   //alert(index)
   //alert(JSON.stringify(controller_values))

   temp = [$("#valve_controllera").val(), controller_values[$("#valve_controllera").val()][index] ]
   working_data["controller_pins"][working_index][ valve_index] = temp
   $("#edit_a_valve").hide()
   generate_valve(working_index, working_data)
   $("#edit_a_step").show();

}

function valve_panel_cancel()
{

    $("#edit_a_valve").hide();
    $("#edit_a_step").show();
}

function find_current_controller()
{
   var i;
   var current_controller;
   
   current_controller = current_valve[valve_index][0]; 
   
   for( i= 0; i< controller_list.length; i++ )
   {
       if( controller_list[i] == current_controller)
       {
        
          return  i;
       }
       else
       {
          ; // do nothing
       }

   }
   return 0;
}







function refresh_valve( controller, valve_index)
{
    
    
    
       
    var select_pins = controller_labels[controller]
    
    $("#valve_valvea").empty()
    for( i = 0; i < select_pins.length; i++)
    {
        
        $("#valve_valvea").append($("<option></option>").val(i+1).html(select_pins[i]));
    } 

    $("#valve_valvea")[0].selectedIndex = valve_index;
    $("#valve_valvea").selectmenu("refresh")

}

function load_valve( step_indexa, valve_indexa , add_flag )
{ 
    var i;
    var temp_value;
    var name;
    var length;
    var controller_index;
    var temp_value; 
    var j;
    var valve_location;

    
    if( typeof add_flag == 'undefined')
    {
        add_flag = false;
    }
   
    step_index = step_indexa;
    valve_index = valve_indexa;

    $("#edit_a_valve").show()
    $("#edit_a_step").hide()
  
    current_valve = working_data["controller_pins"][working_index]

    step_valves =[]
    for( i=0; i<current_valve.length; i++)    
    {
       temp_value = current_valve[i]
       step_valves.push(temp_value)
    }
     
    controller_labels = {}
    controller_list   = []
    controller_values = {}
    for( i=0; i<pin_list.length; i++ )
    {
       name = pin_list[i]["name"]
       length = pin_list[i]["pins"].length;
         
       controller_labels[name] = []
       controller_list.push(name)
       controller_values[name] = []
       
       count = 0;
       for( j = 0; j < length; j++)
       {
            
            temp_value = pin_list[i]["pins"][j];

           if( ( add_flag == false ) && match_current_valve(j,name) )
           {
             
              alert("match_index "+ j)
              valve_location = count;
              controller_labels[name].push("I/O:  "+(j+1) +"    Description : "+temp_value);
              controller_values[name].push(j+1)
              count = count +1;
           }
           else if( match_step_valve(j,name) )
           {
               
              ; //controller_labels[name].push("I/O:  "+j+ "    ----- Defined in Irrigation Step Donot Select  ");
            }

           else
            {
              controller_labels[name].push("I/O:  "+(j+1)+ "    Description : "+temp_value);
              controller_values[name].push(j+1)
              count = count +1;
            }

      }

    }

    controller_index = find_current_controller()
    $("#valve_controllera").empty()
    
    for( i= 0; i< controller_list.length; i++)
    {
       $("#valve_controllera").append($("<option></option>").val(controller_list[i]).html(controller_list[i]));
    }
   
    $("#valve_controllera")[0].selectedIndex = controller_index;
    $("#valve_controllera").selectmenu("refresh")
    
    var select_pins = controller_labels[controller_list[controller_index]]
    
    $("#valve_valvea").empty()
    for( i = 0; i < select_pins.length; i++)
    {
        
        $("#valve_valvea").append($("<option></option>").val(i+1).html(select_pins[i]));
    } 
   
    $("#valve_valvea")[0].selectedIndex = valve_location;
    $("#valve_valvea").selectmenu("refresh")
 
}


function match_current_valve( index, controller )
{
  if( controller != current_valve[valve_index][0] )
  {
      return false;
  }
  else
  {
     if( (index+1) == current_valve[valve_index][1] )
     {
       return true;
      }
  }
  return false;


}

function match_step_valve( index, controller )
{
   var i;

   for( i = 0; i < step_valves.length; i++ )
   {
       
       if( ( step_valves[i][0] == controller ) && ( step_valves[i][1] == (index +1) ) )
       {
          
           return true; 
       }
   } 
   return false;
}

function initialize_edit_a_valve_panel()
{

   $("#edit_a_valve").hide()
   $("#master_save").hide() 
   $( "#edit_valve_cancel" ).bind( "click", valve_panel_cancel );
   $( "#edit_valve_save" ).bind( "click", valve_panel_save );
   $( "#valve_controllera" ).bind( "change", valve_panel_controller_select );
   $( "#valve_valvea").bind("change",valve_panel_valve_select);
}
