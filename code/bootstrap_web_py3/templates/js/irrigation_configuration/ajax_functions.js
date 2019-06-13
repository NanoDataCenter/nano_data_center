

function make_change_delete( schedule, data )
{

   make_change( "delete",schedule,data,"Do you want to delete schedule "+schedule )
}


function  make_change_update( schedule_name,data,confirmation_string)
{

   make_change("update",schedule_name,data, confirmation_string)
}

function make_change( action,schedule,data, confirmation_string)
{
 
       var json_data = {}
       var json_string;
       var url;

       json_object = {}
       json_object["action"]   = action
       json_object["schedule"] = schedule
       json_object["data"]     = schedule_data;
       var json_string = JSON.stringify(json_object);


      ajax_post_confirmation('/ajax/update_schedule', json_object, confirmation_string,
                                                "Changes Made","Changes Not Made") 
      setTimeout(function() { location.reload() },2000)

}                                      

