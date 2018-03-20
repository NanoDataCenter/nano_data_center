$(document).ready(
 function()
 {
 function eto_functions()
 {
 
     $( "#change_eto_flag" ).bind( "click", function(event, ui) 
     {

       var json_data = {}
       json_object = {}
       json_object["hash_name"] = "CONTROL_VARIABLES"
       json_object["key_list"] = {}
       json_object["key_list"]["ETO_MANAGE_FLAG"]  = $("#eto_flag").val();

       var json_string = JSON.stringify(json_object);

       var result = confirm("Do you want to make reset eto management flag ?");
       if( result == true )
       {    // making update
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/set_redis_hkeys',
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    data: json_string,
	            contentType: "application/json",
                    success: function () 
		    {
                       alert("Changes Made");
		       
		       
                    },
                    error: function () 
		    {
                       alert('/ajax/set_redis_hkeys'+"Server error");
		      
		       
                    }
              })
       }// if    
	
     } );
     
 
      

	
 
     
    var ajax_eto_flag_success = function(data)
    {
    
     
      $("#eto_flag")[0].selectedIndex = data.eto_flag;
      $("#eto_flag").selectmenu();
      $("#eto_flag").selectmenu("refresh");      

       
    }
    
    function get_eto_data()
    {

        json_object = {}
        json_object["hash_name"] = "CONTROL_VARIABLES"
        json_object["key_list"] = ["ETO_MANAGE_FLAG" ]
        var json_string = JSON.stringify(json_object);

    $.ajax(
         {
                    type: "POST",
                    url: '/ajax/get_redis_hkeys',
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    success: ajax_eto_flag_success,
                    data: json_string,
	            contentType: "application/json",
              
                    error: function () 
		    {
                       alert('/ajax/get_redis_hkeys' +"   "+"access unsuccessfull");
		       
		       
                    }
       }); 
 
    }
    
    get_eto_data()
   


 

       
     
  } // end of function
  
  eto_functions()
 }
)
