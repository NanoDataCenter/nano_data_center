

function initialize_time_control()
{
   $( "#day_sched" ).bind( "click", select_day_scheduling_method );

}

function select_day_scheduling_method()
{
    
 if($("#day_sched").val() == 0)
   {
      $("#dow_times").show();
      $("#day_mod_times").hide();
   }
   else
   {
      $("#day_mod_times").show();
      $("#dow_times").hide(); 
   }
    
}
      
function show_time_panel()
{
   $("#start_time").show();
}

function hide_time_panel()
{
   $("#start_time").hide();
}


function time_load_controls(working_data)
{
  
   if( !("schedule_enable" in working_data))
   {
      
      working_data["schedule_enable"] = true
    
   }     
    
    if( !('day_flag' in working_data))
   {

      working_data["day_flag"] = 0
    
   } 
    
   if( !('day_flag' in working_data))
   {

      working_data["day_flag"] = 0
    
   }
   if( working_data["day_flag"] == 0)
   {
      $("#dow_times").show();
      $("#day_mod_times").hide();
   }
   else
   {
      $("#day_mod_times").show();
      $("#dow_times").hide(); 
   }
   if( !('day_div' in working_data))
   {
      
      working_data["day_div"] = 0
    
   }   
   if( !('day_mod' in working_data))
   {
      
      working_data["day_mod"] = 0
    
   }
   
   $("#day_sched")[0].selectedIndex =  working_data["day_flag"];
   $("#day_div")[0].selectedIndex =  working_data["day_div"]-1;
   $("#day_mod")[0].selectedIndex =  working_data["day_mod"];
   
   
   temp_start_times = working_data["start_time"]
   temp_end_times   = working_data["end_time"]
   temp_index       = temp_start_times[0]*4;
   temp_index       += temp_start_times[1]/15;
   $("#starting_time")[0].selectedIndex = temp_index;
   
   temp_index       = temp_end_times[0]*4;
   temp_index += temp_end_times[1]/15;
   $("#ending_time")[0].selectedIndex = temp_index;
   
   temp_dow = working_data["dow"]
   if( temp_dow[0] != 0 ){ $("#sunday").prop( "checked", true ) } else {$("#sunday").prop( "checked", false ) }
   if( temp_dow[1] != 0 ){ $("#monday").prop( "checked", true ); } else {$("#monday").prop( "checked", false ) }
   if( temp_dow[2] != 0 ){ $("#tuesday").prop( "checked", true ) } else {$("#tuesday").prop( "checked", false ) }
   if( temp_dow[3] != 0 ){ $("#wednesday").prop( "checked", true ) } else {$("#wednesday").prop( "checked", false ) }
   if( temp_dow[4] != 0 ){ $("#thursday").prop( "checked", true ) } else {$("#thursday").prop( "checked", false )}
   if( temp_dow[5] != 0 ){ $("#friday").prop( "checked", true )} else {$("#friday").prop( "checked", false ) }
   if( temp_dow[6] != 0 ){ $("#saturday").prop( "checked", true ) } else {$("#saturday").prop( "checked",false  )}
   
   if( working_data["schedule_enable"] == true ){ $("#enable_schedule").prop( "checked", true ) } else {$("#enable_schedule").prop( "checked",false  )}
}
 

function dow_filter( name )
{
     name = "#"+name
     var temp = $(name).prop( "checked" )
   
     if( temp == true )
     {
         return 1;
     }
     return 0;
}



function get_data_time_page( working_data)
{

     dow = []
     dow.push( dow_filter("sunday") )
     dow.push( dow_filter("monday") )
     dow.push( dow_filter("tuesday") )
     dow.push( dow_filter("wednesday") )
     dow.push( dow_filter("thursday") )
     dow.push( dow_filter("friday"))
     dow.push( dow_filter("saturday") )

     
     
     working_data["dow"] = dow;     
     working_data["start_time"]  =  eval($("#starting_time").val()) 
     working_data["end_time"] =  eval($("#ending_time").val()) 
     working_data["day_flag"] =  $("#day_sched").val() -1
     working_data["day_div"]  =  $("#day_div").val() -1
     working_data["day_mod"]  =  $("#day_mod").val() -1
     if( $("#enable_schedule").is(":checked") == true )
     {
        working_data["schedule_enable"] = true
     }
     else
     {
        working_data["schedule_enable"] = false
     }
}
