/*
**
** File:  manage_parameters.js
**
**
*/
function load_data_success()
{    
  
  data = JSON.parse(control_data_json )
  if( typeof data.RAIN_FLAG === "undefined" ){data.RAIN_FLAG = 0}
  $("#rain_flag")[0].selectedIndex = data.RAIN_FLAG

  
  if( typeof data.ETO_MANAGE_FLAG === "undefined" ){data.ETO_MANAGE_FLAG = 1}
  $("#eto_flag")[0].selectedIndex = data.ETO_MANAGE_FLAG;

  
  if( typeof data.FLOW_CUT_OFF === "undefined" ){data.FLOW_CUT_OFF = 30}
  $("#max_rate").val(data.FLOW_CUT_OFF)
  max_rate_change()
    
   if( typeof CLEANING_INTERVAL === "undefined" ){data.CLEANING_INTERVAL = 15000}
   $("#cleaning_interval").val(data.CLEANING_INTERVAL)
   $( "#cleaning_value" ).html(data.CLEANING_INTERVAL);
   cleaning_interval_change() 
           
}
function load_data()
{
   json_object = {}
   json_object["hash_name"]  = "CONTROL_VARIABLES"
   json_object["key_list"] = ["rain_day","ETO_MANAGE_FLAG","FLOW_CUT_OFF","CLEANING_INTERVAL" ]

   ajax_post_get("/ajax/redis_hget", json_object, load_data_success, "Initialization Data Not Loaded!!!!!" ) 
}
function change_rain_day_flag(event, ui)
{
   key = "rain_day"
   value = $("#rain_flag").val();
   general_change_function(key,value,"change rain day flag?")

}

function change_eto_flag(event, ui)
{
   key = "ETO_MANAGE_FLAG"
   value = $("#eto_flag").val();
   general_change_function(key,value,"change eto management?")
}
       
function change_max_flow_cut_off(event, ui)
{

   key = "FLOW_CUT_OFF"
   value = $("#max_rate").val()
   general_change_function(key,value,"change max flow cut off?")

}

function change_gallon_trigger(event, ui)
{

   key = "CLEANING_INTERVAL"
   value = $("#cleaning_interval").val()
   general_change_function(key,value,"clean filter threshold?")

}

function general_change_function( key, value,confirmation_message )
{
   temp = {}
   temp["redis_key"] = "CONTROL_VARIABLES"
   temp["hash"] = key
   temp["value"] = value
   json_object = [temp]  
   
   ajax_post_confirmation("/ajax/redis_hset", json_object, confirmation_message, 
                                         "CHANGES MADE", "Data Not Saved!!!!!" )
   
}

function max_rate_change(event,ui)
{
    
    $("#flow_rate_display").html("Flow Limit to Initiate Cut Off (GPM)  " +$("#max_rate").val())  
    
}
function cleaning_interval_change(event,ui)
{
    
    $("#cleaing_interval_display").html("Gallons to Initiate Automatic Cleaning)  " +$("#cleaning_interval").val())  
    
}

$(document).ready(
function()
{

   $( "#change_rain_flag" ).bind( "click", change_rain_day_flag )
   $( "#change_eto_flag" ).bind( "click", change_eto_flag       )
   $( "#cut_off_trigger_id").bind("click",change_max_flow_cut_off)
   $( "#change_gallon_trigger").bind("click",change_gallon_trigger)
   $("#max_rate").on("input",  max_rate_change) 
   $("#cleaning_interval").on("input",  cleaning_interval_change)
   load_data_success()

}
)

