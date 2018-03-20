$(document).ready(
 function()
 {
     var overall_data;
     var linear_structure;
     var json_string;
     var conversion_factor;
     
/*     
     function modbus_statistics_success( data )
     {
        var keys;
        var temp;
        var html;
        var keys;
        var addresses;
        var count;

        count            = 0;
        overall_data     = data
        linear_structure = []

        $("#modbus_counter").empty();
        keys = Object.keys(data)
        html = "";
        html +=  "<h3>Select to clear  </h3>";
	html += '<div data-role="controlgroup">';
          
        for( i = 0; i < keys.length; i++ )
        {
            temp_data_string   = data[keys[i]]
            temp_data_string1   = JSON.parse( temp_data_string )
            temp_data_object    = JSON.parse( temp_data_string1 )
            addresses           = Object.keys( temp_data_object )
            for( j = 0; j < addresses.length; j++ )
            {
              element_data = temp_data_object[addresses[j]]
              element_data.modbus_address = addresses[j]
              element_data.udp_address    = keys[i]
              linear_structure.push(element_data)             
              html +=   '<label for=id'+count+'  >Station '+addresses[j]+"      Total Msgs -->"+element_data.counts+"     Retries -->"+element_data.failures+"    Message Errors -->"+element_data.total_failures+" " +"</label>"
	      html +=   '<input type=checkbox   id=id'+count+' />';
              count = count +1
            }
        }
        html += "</div>";
        count = 0
        $("#modbus_counter").append (html)
        for( i = 0; i < keys.length; i++ )
        {
            for( j = 0; j < addresses.length; j++ )
            {
              $("#id"+count).checkboxradio();
              $("#id"+count).checkboxradio("refresh");
              count = count +1;
            }
               
        }	 

          

       

          
   } 

*/    
   
     $("#clear_modbus_counter").bind("click",function(event,ui)
     {
       var json_data = {}
       json_object = {}
       json_object["object_name"] = "MODBUS_STATISTICS:"+$("#interface_type").val()
      
       var json_string = JSON.stringify(json_object);
        

         result = confirm("Do you want to make change selected modbus counters");
	 
         if( result == true )
         { 
	  
      
	   
	   // making update
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/delete_element',
	            contentType: "application/json",
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    data: json_string,
                    success: function () 
		    {
                       alert("Changes Made");
		       load_data() 
                    },
                    error: function () 
		    {
                       alert('/ajax/delete_element'+"  Server Error Change not made");
		       
		       
                    }
              })
       }// if     
   
  
});


     
     
     
     function modbus_statistics_success( data )
     {
        var keys;
        var temp;
        var html;
        var keys;
        var addresses;
        var count;
        count            = 0;
        overall_data     = data
        
        $("#modbus_counter").empty();
        keys = Object.keys(data)
        html = "";
        html +=  "<h3>Modbus Results for Interface "+$("#interface_type").val() +"  </h3>";
	html += '<ol>';

        for( i = 0; i < keys.length; i++ )
        {
            temp_data_string   = data[keys[i]]
           
            element_data   = JSON.parse( temp_data_string )
            
            
                       
              html +=   '<li>Address '+element_data.address+"      Total Msgs -->"+element_data.counts+"     Retries -->"+element_data.failures+"    Message Errors -->"+element_data.total_failures+" " +"</li>"
	     
              count = count +1
           
        }
        html += "</ol>";
    $("#modbus_counter").append (html)
          

       

          
   }     
      
   function load_data(event, ui) 
   {
     
 
      
      
      var json_data = {}
      json_object = {}
      json_object["hash_name"] = "MODBUS_STATISTICS:"+$("#interface_type").val()
      
      var json_string = JSON.stringify(json_object);
    
 
       
       
      $.ajax
      ({
	
                    type: "POST",
                    url: '/ajax/get_redis_all_hkeys',
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    
                    success: modbus_statistics_success, 
	            contentType: "application/json",
		    data: json_string,
                    error: function () 
		    {
                       alert('/ajax/get_redis_all_hkeys'+"  Server Error Change not made");
		   
		       
                    }
      })
          
	
   }
       

   load_data();

   $("#interface_type").bind("click",function(event,ui)
   {
     
      load_data();
      
   });

   $("#refresh").bind("click",function(event,ui)
   {
     
      load_data();
      
   });
 });
