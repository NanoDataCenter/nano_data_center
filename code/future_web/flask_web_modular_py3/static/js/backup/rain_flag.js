$(document).ready(
 function()
 {
function rain_day_functions()
{
   
    $( "#change_rain_flag" ).bind( "click", function(event, ui) 
     {
 
       var json_data = {}

       json_object = {}
       json_object["hash_name"] = "CONTROL_VARIABLES"
       json_object["key_list"] = {}
       json_object["key_list"]["rain_day"]  = $("#rain_flag").val();
    
       var json_string = JSON.stringify(json_object);
 
       var result = confirm("Do you want to change rain flag ?");
       if( result == true )
       {    // making update
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/set_redis_hkeys',
                    dataType: 'json',
                    async: true,
                    contentType: "application/json",
                    data: json_string,
                    success: function () 
		    {
                       alert("Changes Made");
		       
		       
                    },
                    error: function () 
		    {
                       alert('/ajax/set_redis_hkeys'+"  Server Error Change not made");
		      
		       
                    }
              })
        }// if    
	
     } );
     
 
	
 
     
    var rain_flag_success = function(data)
    {
      var rain_flag;
    
      
    
      $("#rain_flag")[0].selectedIndex = data.rain_day;
      $("#rain_flag").selectmenu();
      $("#rain_flag").selectmenu("refresh");  
           
    }

    function get_rain_data()
    {
    
       json_object = {}
       json_object["hash_name"] = "CONTROL_VARIABLES"
       json_object["key_list"] = ["rain_day"]
       
       var json_string = JSON.stringify(json_object);

    $.ajax(
         {
                    type: "POST",
                    url: '/ajax/get_redis_hkeys',
                    dataType: 'json',
                    async: true,
                    contentType: "application/json",
                    data: json_string,

                    //json object to sent to the authentication url
                    success: rain_flag_success,
              
                    error: function () 
		    {

                       alert("/ajax/get_redis_keys" +"   "+"access unsuccessfull");
		       
		       
                    }
       }); 
 
    }
   get_rain_data()

}
  rain_day_functions()
 }
)
