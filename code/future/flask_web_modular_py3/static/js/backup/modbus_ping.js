$(document).ready(
 function()
 {
     
     

     $("#interface_type").bind("click",function(event,ui)
     {
        remote_dict = remotes[ $("#interface_type").val()]
        update_remotes(remote_dict)
      
     });


     display_results = function(data)
     {
         
         $("#ping_result").val(data)

     } 
   
     $("#ping_device").bind("click",function(event,ui)
     {
       
    
	
	 var json_object;
	 var json_string;
	 json_object = {}
         json_object["interface"] = $("#interface_type").val()
         json_object["remote"]    = $("#remote_unit").val()


         $("#ping_result").val("")
   
         json_string = JSON.stringify(json_object);
         result = confirm("Do you want to ping selected devices");
	 
         if( result == true )
         { 
	  
      
	   
	   // making update
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/ping_modbus_device',
	            contentType: "application/json",
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    data: json_string,
                    success: display_results,

                    error: function () 
		    {
                       alert('/ajax/ping_modbus_device'+"  Server Error Change not made");
		       
		       
                    }
              })
          
       }
  
     });


 

        
     
     

    function update_remotes( interface_id )
    {
         
         remotes_list = remotes[interface_id ]
         $("#remote_unit").empty()
         for( var i = 0; i < remotes_list.length; i++ )
	 {

	  if( remotes_list[i] != "255" )
          {
             $("#remote_unit").append('<option value='+remotes_list[i]+'>'+remotes_list[i]+'</option>');
          }	
	
	 }
       
    }
    interfaces = JSON.parse(interfaces_json)   
    remotes    = JSON.parse(remotes_json)
    update_remotes( interfaces[0] )

  
 });
