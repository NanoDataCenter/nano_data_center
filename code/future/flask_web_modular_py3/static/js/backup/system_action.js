

$(document).ready(
 function()
 {

  function find_index( choice )
  {
    for( i = 0; i < system_actions.length;i++)
    {    
         if( choice == system_actions[i].name )
         {
           return i;
         }
    }
    return -1;
  }
  function add_function(event, ui)
  {


      choice = $("#action_select").val()

      index  = find_index(choice)

      $("#action_select")[0].selectedIndex = 0;
      $("#action_select").selectmenu();
      $("#action_select").selectmenu("refresh")
      if( index >= 0 )
      {
          working_data = system_actions[index]
          $("#edit_panel").show();
          $("#choice_action").hide();
          $("#edit_panel_header").html("Modify Setup For Action: "+working_data.name )
          working_data = system_actions[index] 
       
          if( working_data.enable == "true")
          {
            $("#enable_checkbox").attr("checked",true).checkboxradio("refresh");
          }
          else
          {
            $("#enable_checkbox").attr("checked",false).checkboxradio("refresh");
          }

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


  function save_function(event, ui)
  {
     // index contains correct index
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
     if( $("#enable_checkbox").is(":checked")== true )
     {
        working_data.enable = "true"
     }
     else
     {
        working_data.enable = "false"
     }
     
     
     make_change() 


     $("#edit_panel").hide();
     $("#choice_action").show();
  }

function make_change() 
{
 
       var json_data = {}
       var json_string;
       var url;
   

       var result = confirm("Do you want to change schedule data ?");
       if( result == true )
       {    
            system_actions[index] = working_data
            var json_string = JSON.stringify(system_actions);
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/save_app_file/system_actions.json',
                    dataType: 'json',
                    async: true,
                    contentType: "application/json",
                    data: json_string,
                    success: function () 
		    {
                       alert("changes updated")
  
                    },
                    error: function () 
		    {
                       alert('/ajax/save_app_file/system_actions.json'+"  Server Error Change not made");

		
		       
                    }
              })
      }
}




  function cancel_function(event, ui)
  {
   
     $("#edit_panel").hide();
     $("#choice_action").show();
  }

  $("#edit_panel_save").bind("click",save_function );
  $("#edit_panel_cancel").bind("click",cancel_function);
  $("#edit_panel").hide();
  $( "#action_select" ).bind( "change", add_function );


 }
)
