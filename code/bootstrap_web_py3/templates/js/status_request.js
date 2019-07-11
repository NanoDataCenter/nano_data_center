 
function status_request_function()
{
   json_object = {}

   
   ajax_get( '/ajax/status_update', "Data Not Fetched", status_update )
 
   
}
       
function status_update( data )
{
       var temp
       var temp_1
       var tempDate
       
       //alert(JSON.stringify(data))
       var date = new Date( data["TIME_STAMP"]  * 1000);
       tempDate = new Date()
       
       $("#time_stamp").html("Time:  "+tempDate.toLocaleDateString() + "   " + tempDate.toLocaleTimeString() )

       $("#controller_time_stamp").html("Ctr Time: "+ date.toLocaleDateString() + "   " + date.toLocaleTimeString() )
       //$("#flow_rate").html("GPM:  "+parseFloat(data.global_flow_sensor_corrected).toFixed(2));
       
       $("#schedule").html("Schedule: "+data["SCHEDULE_NAME"])
       $("#step").html("Step:   "+data["STEP"])
       $("#time").html("Step Time:  "+data["RUN_TIME"])
       $("#duration").html("ELASPED_TIME: "+ data["ELASPED_TIME"]) 
       $("#rain_day").html("Rain Day: "+data["RAIN_FLAG"])
       //$("#coil_current").html("Coil ma: "+parseFloat(data.coil_current).toFixed(2))
       $("#master_valve").html("Master Valve: "+data.MASTER_VALVE_SETUP )
       $("#eto_management").html("ETO Management: "+data.ETO_MANAGEMENT )
 
       $("#suspend").html("Suspension State:  "+data.SUSPEND )
       $("#clean_filter_limit").html("Filter Cleaning Limit (Gallon):  "+parseFloat(data.CLEANING_INTERVAL).toFixed(2) )
       $("#clean_filter_value").html("Filter Cleaning Accumulation (GPM):  "+parseFloat(data.cleaning_sum).toFixed(2 ))


}



function system_state_init()
{    var g,h,i
     var alarm_data;
     var  queue_interval_id;
     var  nintervalId;
     var data = [];
     var conversion_factor_index;
     var conversion_factor;
     var conversion_factor_array;


 
    

   $( "#status_panel"  ).bind({ popupafteropen: status_request_function })
   
   

  } 


