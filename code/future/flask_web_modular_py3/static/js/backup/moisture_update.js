$(document).ready(

 

    function()
    {
        var temp_index = 0
        var json_object = {}
        var json_string = ""
        var result    = 0

        function moisture_update()
        {
   
            $( "#get_results" ).bind( "click", function(event, ui) 
            {  
                 var temp_index
        
                 temp_index = $("#moisturecontroller_id")[0].selectedIndex;
	
                 json_object = {"index":temp_index}
                 json_string = JSON.stringify(json_object);
                 result = confirm("Do you want to update moisture readings ?");
                 if( result == true )
                 {    // making update
                      $.ajax
                     ({
                         type: "POST",
                         url: '/ajax/start_moisture_conversion',
                         dataType: 'json',
                         async: true,
                         contentType: "application/json",
                         data: json_string,
                         success: function () 
		         {
                             $("#data").empty();
                             $("#data").html("<center><h1>Waiting For New Measurements</h1></center>")
                             setTimeout(get_data, 12000)
                         },
                         error: function () 
		         {
                            alert('/ajax/soil_moisture_update'+"  Server Error Change not made");
		         }
                      }) // end of ajax function
                  }// end of if
            }
            ) // end of click function
   
           function get_data( )
           {

            
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/soil_moisture_update',
                    dataType: 'json',
                    async: true,
                    contentType: "application/json",
                    data: json_string,
                    success: function (data) 
		    {
                       $("#data").html(data)
		       
		       
                    },
                    error: function () 
		    {
                       alert('/ajax/get_moisture_data'+"  Server Error Change not made");
		      
		       
                    }
              })

         }
        
         json_object = {"index":0}
         json_string = JSON.stringify(json_object);
         get_data() // initialize first screen
   
    }
    moisture_update()
     });
        
 
    




