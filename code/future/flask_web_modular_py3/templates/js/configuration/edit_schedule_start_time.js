

function initialize_time_control()
{
  ; // nothing for now
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
   temp_start_times = working_data["start_time"]
   temp_end_times   = working_data["end_time"]
   temp_index       = temp_start_times[0]*4;
   temp_index       += temp_start_times[1]/15;
   $("#starting_time")[0].selectedIndex = temp_index;
   $("#starting_time").selectmenu("refresh")
   temp_index       = temp_end_times[0]*4;
   temp_index += temp_end_times[1]/15;
   $("#ending_time")[0].selectedIndex = temp_index;
   $("#ending_time").selectmenu("refresh")
   temp_dow = working_data["dow"]
   if( temp_dow[0] != 0 ){ $("#sunday").prop( "checked", true ).checkboxradio( "refresh" ); } else {$("#sunday").prop( "checked", false ).checkboxradio( "refresh" ); }
   if( temp_dow[1] != 0 ){ $("#monday").prop( "checked", true ).checkboxradio( "refresh" );; } else {$("#monday").prop( "checked", false ).checkboxradio( "refresh" ); }
   if( temp_dow[2] != 0 ){ $("#tuesday").prop( "checked", true ).checkboxradio( "refresh" ); } else {$("#tuesday").prop( "checked", false ).checkboxradio( "refresh" ); }
   if( temp_dow[3] != 0 ){ $("#wednesday").prop( "checked", true ).checkboxradio( "refresh" ); } else {$("#wednesday").prop( "checked", false ).checkboxradio( "refresh" ); }
   if( temp_dow[4] != 0 ){ $("#thursday").prop( "checked", true ).checkboxradio( "refresh" ); } else {$("#thursday").prop( "checked", false ).checkboxradio( "refresh" ); }
   if( temp_dow[5] != 0 ){ $("#friday").prop( "checked", true ).checkboxradio( "refresh" );} else {$("#friday").prop( "checked", false ).checkboxradio( "refresh" ); }
   if( temp_dow[6] != 0 ){ $("#saturday").prop( "checked", true ).checkboxradio( "refresh" ); } else {$("#saturday").prop( "checked",false  ).checkboxradio( "refresh" ); }

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


}
