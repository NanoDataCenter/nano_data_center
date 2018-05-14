$(document).ready(
 function()
 {
 function load_irrigation_queue_data()
 {
     var result;
     var schedule_name;
     var flow_sensor;
     var queue_values;
     var json_string;
     

   

   
    $("#refresh_b").bind("click",function(event,ui)
   {
       load_data();
   });


   function getQueueEntries( data )
   {
  
        var temp_index;
        var temp
        var html;

       
       queue_values = data
        $("#queue_elements").empty();
      
       if( data.length == 0 )
       {
        var html = "";
          html +=  "<h3>No Elements in Past Action Queue </h3>";
	  html += '<div data-role="controlgroup">';
	 
	 
       }
       else
       {
        var html = "";
          
	  
          

          for( i = 0; i < data.length; i++ )
          {
            temp = atob(data[i])
            
	    temp  = JSON.parse(temp);
            // create a new javascript Date object based on the timestamp
            // multiplied by 1000 so that the argument is in milliseconds, not seconds
            
            var d = new Date(0); // The 0 there is the key, which sets the date to the epoch
            formatted = d.setUTCSeconds(temp["time"]);
            var formatted = new Date(temp["time"]*1000);
            temp_index = i +1; 
            var flag;  // this is a temporary hack right now
            flag = false;
           
            if( temp["status"] == "RED" )
            {   
                
                html +=   '<div data-role="fieldcontain"  style=background:#ff0000;color:white >' 
                flag = true 
	     
            }
            if( temp["status"] == "YELLOW" )
            {   
                
                html +=   '<div data-role="fieldcontain"  style=background:#ffff00;color:black >'  
	        flag = true
            }
            if( flag == true )
            {
 
            if( temp["data"] != null )
            {
                    temp["data"] = JSON.stringify(temp["data"])
                  
                   html +=   'Event:  '+temp["event"]+"  Time: "+formatted +"              Data: "+temp["data"]+" </div>"
                   
            }
            else
            {
                    html +=   'Event:  '+temp["event"]+"  Time: "+formatted +" </div>"
                    
            }
            }
            
     

           
             
           }
       }
       
      
      $("#queue_elements").append (html)

          
   } 



   function load_data(event, ui) 
   {
      
      json_object = {}
      json_object["list_name"] = reference_queue
      var json_string = JSON.stringify(json_object);
     
        
       
      $.ajax
      ({
	
                    type: "POST",
                    url: '/ajax/get_all_redis_list',
                    dataType: 'json',
                    async: true,
                    data: json_string,
                    success: getQueueEntries, 
                    contentType: "application/json",
                    error: function () 
		    {
                       alert('/ajax/get_all_redis_list'+"  Server Error Change not made");
		   
		       
                    }
      })
          
	
   }    
    
   load_data();
  

}
load_irrigation_queue_data()
 }
)
     
     
     

      

  

  

