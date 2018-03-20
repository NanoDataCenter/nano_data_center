
/*
	<legend>Select ETO Resource:</legend>
        {% for item in eto_data %}
     	   <input type="radio" name="eto_emiter" id="eto_emiter_id_{{loop.index -1}}" value={{loop.index-1}}  />
           {% set label_text = "Controller: "+item.controller+ "  Valve: "+st(item.pin) +" Recharge Rate: "+st(item.recharge_rate) + " Recharge Level: "+st(item.recharge_eto) %}
     	   <label for="eto_emiter_id_{{loop.index-1}}">{{label_text }} </label>
     	{% endfor %}
*/
/*
Server Template is preloading the following javascript objects
            eto_data = {{eto_data_json}}    
            pin_list = {{pin_list_json}}        
*/

site_specific_defaults =
[
["recharge_eto",        .07,"ETO Recharge Level: ",1," inch"],
["crop_utilization",    .8,"Crop Utilization: ",100," %"], 
["sprayer_effiency",    .8,"Sprayer Efficency: ",100," %"] ,
["salt_flush_addition", .1,"Salt Flush Addition: ",100," %"] 
]



reference_value = {}

function validate_field( index, field, default_value )
{
   var value
   if( eto_data.length == 0 )
   {
      value = default_value
   }
   else if( field in eto_data[index] )
   {
      value = eto_data[index][field]
   }
   else
   {
      value = default_value
   } 
   return parseFloat(value)

}

function load_site_specific_control(item, index)
{
   reference_value[item[0]] = validate_field( index, item[0], item[1] )
   $("#"+item[0]).html(item[2]+reference_value[item[0]]*item[3]+item[4] )   
}
function calculate_eto_data( sprayer_rate,
                         tree_radius,
                         sprinkler_efficiency,
                         salt_flush,
                         crop_utilization )

{
        // effective volume is ft3/hr
        // sprayer rate is in Gallons/hr
        // 1 gallon is 0.133681 ft3
        //console.log(sprayer_rate)
        //console.log(tree_radius)
        //console.log(sprinkler_efficiency)
        //console.log(salt_flush)
        //console.log(crop_utilization)
        
        effective_rate = sprayer_rate*sprinkler_efficiency/crop_utilization/(1+salt_flush)
        effective_volume = 0.133681 * effective_rate
        effective_area =  tree_radius*tree_radius*3.14159
        return (effective_volume/effective_area)*12; // converting the eto to inches
}


function refresh_stations(item,index)
{
   
   item["recharge_eto"]  =   reference_value["recharge_eto"]
   item["crop_utilization"]  =   reference_value["crop_utilization"]
   item["sprayer_effiency"]  =   reference_value["sprayer_effiency"]
   item["salt_flush_addition"]  =   reference_value["salt_flush_addition"]
   item["tree_radius"] = validate_field(index, "tree_radius",6.0)
   item["sprayer_rate"] = validate_field(index, "sprayer_rate",14.5)
   item["recharge_rate"] =( calculate_eto_data( item["sprayer_rate"],item["tree_radius"] ,item["sprayer_effiency"],
                        item["salt_flush_addition"],item["crop_utilization"]))
   
  
}

function load_parameters( )
{
  site_specific_defaults.forEach(load_site_specific_control)
  eto_data.forEach(refresh_stations)
  
}




function find_index()
{
   var i;
   for( i=0; i< eto_data.length; i++)
   {
       if( $("#eto_emiter_id_"+i).is(':checked') == true )
       {
          return i;
       }
    }
    return  -1;  // no item selected
}

function main_menu(event,ui)
{
   var index
   var choice

   choice = $("#action-choice").val()

   if( choice == "recharge")
   {
       parameter_class.open(site_specific_defaults[0],reference_value,"Setup Recharge ETO")
   }
   if( choice == "crop_util")
   {
       parameter_class.open(site_specific_defaults[1],reference_value,"Setup Crop Utilization")
   }
   
   if( choice == "salt")
   {
       parameter_class.open(site_specific_defaults[3],reference_value,"Setup Salt Flush")
   }

   
   if( choice == "sprayer")
   {
       parameter_class.open(site_specific_defaults[2],reference_value,"Setup Sprayer Efficiency")
   }

   
   if( choice == "edit")
   {   
       index = find_index()
       if( index >= 0 )
       {

           station_class.open( index, false, eto_data, "#main_panel")
       }       
       else
       {
          set_status_bar("No Resources Selected !!!!")
       }  
   }

   if( choice == "add")
   {   
       station_class.open( index, true, eto_data, "#main_panel")
   }

   if( choice == "delete")
   {
       var result = confirm("Do you wish to delete eto entry?  ");  
       if( result == true )
       {  
           index = find_index()
           if( index >= 0 )
           {
               eto_data.splice(index, 1);
               parameter_url = window.location.href;
               //alert(JSON.stringify(station_control_class.eto_data[index]))

               ajax_post_get('/ajax/save_app_file/eto_site_setup.json', 
                    eto_data,parameter_success_function,"Server Error")             
           }
           else
           {
              set_status_bar("No Resources Selected !!!!")            
           }
     }
   }

   $("#action-choice")[0].selectedIndex = 0;
   $("#action-choice").selectmenu('refresh');
}


function backup_eto_values()
{
  eto_working = JSON.parse(JSON.stringify(eto_data))
}




$(document).ready(
function()
{

   parameter_class = new Parameter_Setup()

   parameter_class.load_controls(parameter_class,"main_panel")
   station_class = new Station_Setup()
   station_class.load_controls(station_class)
   load_parameters()
   $("#action-choice").bind('change',main_menu)
   $("#action-choice")[0].selectedIndex = 0;
   $("#action-choice").selectmenu('refresh');

})


