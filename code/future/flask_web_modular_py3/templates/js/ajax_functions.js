
/*
**
**
** Ajax functions
**
**
*/

function deepCopyObject(input)
{
  return JSON.parse(JSON.stringify(input))
}

function set_status_bar( text )
{
   $("#page_status").text(text)
}

var user_function 
function status_successful( data )
{
   set_status_bar("Current Status: Fetch operation successful")
   user_function(data)
}

function ajax_get( url_path, error_message, success_function )
{
   user_function = success_function
	  $("#page_status").text("Current Status: Operation in Progress")
   $.ajax(
   {
       type: "GET",
       url: url_path,
       dataType: 'json',
       async: true,
       //json object to sent to the authentication url
       success: status_successful,
              
       error: function () 
		    {
           set_status_bar("Current Status: "+error_message)  
		       
		       
      }
   });
}

function ajax_post_confirmation(url_path, data, confirmation_string, 
                                       success_message, error_message )
{
 
   var result = confirm(confirmation_string);  // change this
   if( result == true )
   {
       $("#page_status").text("Current Status: Operation in Progress")

       var json_string = JSON.stringify(data);
       $.ajax ({  type: "POST",
                  url: url_path,
                  dataType: 'json',
	                 contentType: "application/json",
                  async: true,
                  data: json_string,
                  success: function () 
		                {
                       set_status_bar(success_message)

		                 },

                   error: function () 
		                {
                       set_status_bar(error_message) 	                
                  }
           })
   }
}


function ajax_post(url_path, data,  success_message, error_message )
{
 
   var result = true
   if( result == true )
   {
       $("#page_status").text("Current Status: Operation in Progress")

       var json_string = JSON.stringify(data);
       $.ajax ({  type: "POST",
                  url: url_path,
                  dataType: 'json',
	                 contentType: "application/json",
                  async: true,
                  data: json_string,
                  success: function () 
		                {
                       set_status_bar(success_message)

		                 },

                   error: function () 
		                {
                       set_status_bar(error_message) 	                
                  }
           })
   }
}

function ajax_post_get(url_path, data, success_function, error_message) 
{
     var json_string = JSON.stringify(data);
     $("#page_status").text("Current Status: Operation in Progress")
     user_function = success_function

     $.ajax ({  type: "POST",
                  url: url_path,
                  dataType: 'json',
	                 contentType: "application/json",
                  async: true,
                  data: json_string,
                  success: status_successful,

                   error: function () 
		                {
                       set_status_bar("Current Status: "+error_message)  
		                 }
           })
   
}
 
 
