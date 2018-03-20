
var schedule_name = null;


function close_button(event, ui) 
{
          
          $("#define-schedule").show()   
          $("#edit_panel").hide();
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

function save_button(event, ui) 
{
     var i;
     var dow;
     var url


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

     name = working_data["name"]
     schedule_data[name] = working_data;
     schedule_list = Object.keys(schedule_data)
     $("#define-schedule").show()   
     $("#edit_panel").hide();
     make_change(template_type,name) 

 
}


function set_schedule_name( sched_name )

{

   schedule_name = sched_name;
   $("#edit_panel_header").html( "Modify Setup For Schedule: "+sched_name);

}

function generate_steps(working_data)
{
   temp_steps = working_data["steps"]
   temp_pins  = working_data["controller_pins"]
   
   if( temp_steps.length == 0 )
   {
     $("#current_steps").html("<h3>No Steps Defined</h3>")

   }
   else
   {
      temp =  '<fieldset id="valve_list" data-role="controlgroup" >'
          
      
      for( i = 0; i < temp_steps.length; i++ )
      {
          temp1a = "step-"+i+"a"
          temp1 = "step-"+i
          concat_valves = ""
          for( j= 0; j< temp_pins[i].length; j++)
          {
             concat_valves = concat_valves + "( "+temp_pins[i][j][0] +","+temp_pins[i][j][1] +") "
          }
          temp = temp + '<input type="radio" name="edit_step_radio" id="'+temp1a+'"  value="'+temp1+'"/>'
          temp = temp+  '<label for="'+temp1+'">Step: '+(i+1)+'   Run Time: '+temp_steps[i]+"    Valves:    "+concat_valves +" </label> <BR>      "
      }
      temp = temp +'</fieldset>'

      $("#current_steps").html(temp)
 

   }

}


function load_controls( working_data)
{
   var schedule_name;
   var temp_start_times;
   var end_times;
   var temp_index
   var temp_dow
   var temp_steps
   var i
   var temp
   var concat_valves
   

   schedule_name =  working_data["name"]
   $("#edit_panel_header").html( "Modify Setup For Schedule: "+schedule_name );
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
   generate_steps(working_data)
}


function get_schedule_name()
{
    return schedule_name
}


function initialize_edit_functions()
{
  
  $( "#edit_panel_save" ).bind( "click", save_button );
  $( "#edit_panel_cancel" ).bind( "click", close_button );
}



function make_change(action,schedule) 
{
 
       var json_data = {}
       var json_string;
       var url;

       json_object = {}
       json_object["action"]   = action
       json_object["schedule"] = schedule
       json_object["data"]     = schedule_data;
       var json_string = JSON.stringify(json_object);
       url = window.location.href;
       var result = confirm("Do you want to change schedule data ?");
       if( result == true )
       {    // making update
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/update_schedule',
                    dataType: 'json',
                    async: true,
                    contentType: "application/json",
                    data: json_string,
                    success: function () 
		    {
                       window.location.href = url;
  
                    },
                    error: function () 
		    {
                       alert('/ajax/update_schedule'+"  Server Error Change not made");

		       window.location.href = url;
		       
                    }
              })
      }
}
