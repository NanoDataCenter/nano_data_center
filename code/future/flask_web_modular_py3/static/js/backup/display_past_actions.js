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
     

   
     $("#delete_limits").bind("click",function(event,ui)
     {
       
         var mask;
	 var update_flag;
	 var status;
	 var json_object;
	 var json_string;
	 
         status = [];
	 update_flag = 0; 
         for( i=0;i<queue_values.length;i++)
	 {
	  
	   if( $("#qid"+i).is(":checked") == true )
	   {
	     
             
	     status.push(1);
	     update_flag = 1;
	   }
	   else
	   {
	     
	     status.push(0);
	   }
	 }
         if( update_flag == 0 ){ alert("no changes selected"); return; }
           
         json_object = {}
         json_object["list_name"]     = reference_queue
         json_object["index"]         = status 
         json_object["delete_token"]  = "NULL---|||---NULL"   
         json_string = JSON.stringify(json_object);

         result = confirm("Do you want to make selected changes to irrigation queue");
	 
         if( result == true )
         { 
	  
	   
	   // making update
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/delete_redis_list',
                    dataType: 'json',
                    async: true,
	            contentType: "application/json",
                    //json object to sent to the authentication url
                    data: json_string,
                    success: function () 
		    {
                       alert("Changes Made");
		       load_data();
                    },
                    error: function () 
		    {
                       alert('/ajax/delete_redis_list'+"  Server Error Change not made");
		       
		       
                    }
              })
         }// if     
     });
   
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
          html +=  "<h3>Selects select elements to be deleted from queue </h3>";
	  html += '<div data-role="controlgroup">';

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
           
            if( temp["status"] == "RED" )
            {   
                
                html +=   '<div data-role="fieldcontain"  style=background:#ff0000;color:white >'  
	     
            }
            if( temp["status"] == "YELLOW" )
            {   
                
                html +=   '<div data-role="fieldcontain"  style=background:#ffff00;color:black >'  
	       
            }
            if( temp["status"] == "GREEN" )
            {   
                
                html +=   '<div data-role="fieldcontain"  style=background:#00ff00;color:black>'  
	        
            }
 
            if( temp["data"] != null )
            {
                    temp["data"] = JSON.stringify(temp["data"])
                  
                   html +=   '<legend >Event:  '+temp["event"]+"  Time: "+formatted +"              Data: "+temp["data"]+" </legend>"
                   html +=   '<input type=checkbox   id="qid'+i+'"/>';
	           html +=   '<label for="qid'+i+'"  >Click to Select Delete </label>'
                   
            }
            else
            {
                    html +=   '<legend >Event:  '+temp["event"]+"  Time: "+formatted +" </legend>"
                   html +=   '<input type=checkbox   id="qid'+i+'"/>';
	           html +=   '<label for="qid'+i+'"  >Click to Select Delete </label>'
                   
            }

            html +=  '</div>'
          
             
           }
       } // else
      html += "</div>";
     
      $("#queue_elements").append (html)

      for( i = 0; i < data.length; i++ )
      {

        $("#qid"+i).checkboxradio();
        $("#qid"+i).checkboxradio("refresh");
         
      }
          
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
                       alert('/ajax/get_all_redis_list'+"  Post Not Made");
		   
		       
                    }
      })
          
	
   }    
    
   load_data();
  

}
load_irrigation_queue_data()
 }
)
     
     
     

      

  

  

