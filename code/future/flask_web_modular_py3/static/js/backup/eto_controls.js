ref_index = 0;
local_data = 0;



    
function calculate_data()
{
        var soil_array = [.6,.8,1.0,1.15,1.3, 1.4,1.7,2.0,2.25 ]
        var soil_depth_array = [.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0]
        var recharge_ratio_array = [.05,.10,.15 ,.2,.25, .3,.35, .4,.45,.5]
        var sprinkler_efficiency_array = [ 1.0, .95, .90, .85, .80, .75, .70 ]
        var salt_flush_array           = [ 1.0, .95, .90, .85, .80 ]
        var crop_utilization_array      = [ 1.0, .95, .90, .85, .80, .75, .70, .65, .60 ]

  

        var soil_ref 
        var soil_depth 
        var soil_moisture 
        var recharge_ratio 
        var sprayer_rate
        var sprayer_efficiency
        var salt_flush
        var crop_utilization
        var sprayer_radius
        var effective_rate
        var effective_area
        var effective_volume
        var sprinkler_efficiency_array
        var salt_flush_array
        var crop_utilization_array
          
    
       
        
      
       
        soil_ref = soil_array[ local_data["soil_type_index" ] ]
        
        soil_depth = soil_depth_array[ local_data["soil_depth_index" ] ]
        
        soil_moisture = soil_ref*soil_depth
        
        recharge_ratio = recharge_ratio_array[ local_data["recharge_ratio_index"] ]
        
        local_data["recharge_eto"] = soil_moisture*recharge_ratio
        
        
        sprayer_radius = (local_data["sprayer_radius_index"]*.5)+.5;
        sprayer_rate   = (local_data["sprayer_rate_index"] ) +1;
        sprayer_efficiency  =  sprinkler_efficiency_array[ local_data["sprayer_efficiency_index"] ]
        salt_flush          =  salt_flush_array[ local_data["salt_flush_index"] ]
        crop_utilization    =  crop_utilization_array[local_data["crop_utilization_index"] ]


           
        effective_rate = sprayer_rate*sprayer_efficiency/crop_utilization*salt_flush
        effective_volume = 0.133681 * effective_rate*12.
        effective_area =  sprayer_radius*sprayer_radius*3.14159
        local_data["recharge_rate"] = (effective_volume/effective_area)
        
        $("#eto_capacity_label").html("Soil Capacity (inches): "+local_data["recharge_eto"].toFixed(2) +"<BR>ETO recharge rate (inches/hour): "+local_data["recharge_rate"].toFixed(2)+ "  </h4>" )
  
}

function add_controls()
{
   
   add_flag  = true;
   ref_index = eto_data.length;
   load_controller_valve();
   local_data = {}
   local_data["soil_type_index"]                 = $("#soil_type_id")[0].selectedIndex            
   local_data["soil_depth_index"]               = $("#soil_depth_id")[0].selectedIndex         
   local_data["recharge_ratio_index"]           = $("#recharge_ratio_id")[0].selectedIndex        
   local_data["sprayer_radius_index"]           = $("#sprayer_radius_id")[0].selectedIndex         
   local_data["sprayer_rate_index"]             = $("#sprayer_rate_id")[0].selectedIndex           
   local_data[ "sprayer_efficiency_index"]      = $("#sprayer_efficiency_id")[0].selectedIndex    
   local_data["salt_flush_index"]               = $("#salt_flush_id" )[0].selectedIndex          
   local_data["crop_utilization_index"]         = $("#crop_utilization_id")[0].selectedIndex     
   local_data["controller"] = $("#valve_controllera").val()
   valve_panel_valve_select()
   calculate_data()
}





function load_controls( eto_index )
{
  add_flag  = false;
  ref_index = eto_index;
  local_data = JSON.parse(JSON.stringify(eto_data[ref_index]))
  $("#soil_type_id")[0].selectedIndex           =  local_data["soil_type_index"] 
  $("#soil_depth_id")[0].selectedIndex          =  local_data["soil_depth_index"] 
  $("#recharge_ratio_id")[0].selectedIndex      =  local_data["recharge_ratio_index"] 
  $("#sprayer_radius_id")[0].selectedIndex      =  local_data["sprayer_radius_index"] 
  $("#sprayer_rate_id")[0].selectedIndex        =  local_data["sprayer_rate_index"] 
  $("#sprayer_efficiency_id")[0].selectedIndex  =  local_data[ "sprayer_efficiency_index"] 
  $("#salt_flush_id" )[0].selectedIndex         =  local_data["salt_flush_index"] 
  $("#crop_utilization_id")[0].selectedIndex    =  local_data["crop_utilization_index"] 
  $("#soil_type_id").selectmenu("refresh");
  $("#soil_depth_id").selectmenu("refresh");
  $("#recharge_ratio_id").selectmenu("refresh"); 
  $("#sprayer_radius_id").selectmenu("refresh");
  $("#sprayer_rate_id").selectmenu("refresh");  
  $("#sprayer_efficiency_id").selectmenu("refresh"); 
  $("#salt_flush_id" ).selectmenu("refresh");  
  $("#crop_utilization_id").selectmenu("refresh");   
  calculate_data()
  
}



function load_controller_valve(  )
{ 
    var i;
    var temp_value;
    var name;
    var length;
    
    var temp_value; 
    var j;
    var valve_location;

     
    controller_labels = {}
    controller_list   = []
    controller_values = {}
    for( i=0; i<pin_list.length; i++ )
    {
       name   = pin_list[i]["name"]
       length = pin_list[i]["pins"].length;
         
       controller_labels[name] = []
       controller_list.push(name)
       controller_values[name] = []
       
       count = 0;
       for( j = 0; j < length; j++)
       {
            
           temp_value = pin_list[i]["pins"][j];

           if( match_step_valve(j,name) )
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

    
    $("#valve_controllera").empty()
    
    for( i= 0; i< controller_list.length; i++)
    {
       $("#valve_controllera").append($("<option></option>").val(controller_list[i]).html(controller_list[i]));
    }
    $("#valve_controllera").selectmenu("refresh");
    load_pins();
    valve_panel_controller_select();
    valve_panel_valve_select();
 
}

function load_pins()
{
    var controller_index;

    controller_index = $("#valve_controllera")[0].selectedIndex;
    var select_pins = controller_labels[controller_list[controller_index]]
    
    $("#valve_valvea").empty()
    for( i = 0; i < select_pins.length; i++)
    {
        
        $("#valve_valvea").append($("<option></option>").val(i+1).html(select_pins[i]));
    } 
   
    
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

   for( i = 0; i < eto_data.length; i++ )
   {
       
       if( ( eto_data[i]["controller"] == controller ) && ( eto_data[i]["pin"] == (index +1) ) )
       {
          
           return true; 
       }
   } 
   return false;
}

function valve_panel_controller_select()
{

 
   local_data["controller"] = $("#valve_controllera").val()
   load_pins();

}

function valve_panel_valve_select()
{

   var index = $("#valve_valvea").val()
   pin = controller_values[$("#valve_controllera").val()][index -1] 
   local_data["pin"] = pin

}


