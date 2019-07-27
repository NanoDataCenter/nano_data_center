$(document).ready(
 function()
 {
function moisture_update()
{
   
    $( "#Click_To_Refresh" ).bind( "click", function(event, ui) 
     {
 
       var json_data = {}

       json_object = {}
    
       var json_string = JSON.stringify(json_object);
 
       var result = confirm("Do you want to update moisture readings ?");
       if( result == true )
       {    // making update
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/soil_moisture_update',
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
                       alert('/ajax/soil_moisture_update'+"  Server Error Change not made");
		      
		       
                    }
              })
        }// if    
	
     } );
 moisture_update();
    
}
	

);
