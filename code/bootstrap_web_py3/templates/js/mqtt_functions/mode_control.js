/*
**
** File:  
**
**
*/

function reset_mqtt_devices(event, ui)
{
  ajax_post_confirmation('/mqtt/mqtt_ajax_reset', {},"MQTT Devices Reset", 
                                         "CHANGES MADE", "Data Not Saved!!!!!" )

}



$(document).ready(
function()
{

   $( "#reset_mqtt_device" ).bind( "click", reset_mqtt_devices )
  

}
)

