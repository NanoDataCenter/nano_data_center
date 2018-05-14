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
     

   



   function getQueueEntries( data )
   {

        var temp_index;
        var temp
        var html;
       
       data.reverse()
       
       queue_values = data
        $("#queue_elements").empty();

       if( data.length == 0 )
       {
        var html = "";
          html +=  "<h3>No Elements in Work Queue </h3>";
	  html += '<div data-role="controlgroup">';
	 
	 
       }
       else
       {
        var html = "<ol>";

	  

          for( i = 0; i < data.length; i++ )
          {

            //temp = atob(data[i])
            temp = data[i]
	    temp  = JSON.parse(temp)
            temp_index = i +1;    
	    
	    html +=   '<li>  Schedule '+temp.schedule_name+"    Step: "+temp.step+"   Run Time: "+temp.run_time +"</li>"
           
             
           }
       } // else
      html += "</ol>";

      $("#queue_elements").append (html)

         
   } 

   function load_data(event, ui) 
   {
     
      json_object = {}
      json_object["list_name"] = "QUEUES:SPRINKLER:IRRIGATION_QUEUE"
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

   $("#refresh_c").bind("click",function(event,ui)
   {
       load_data();
   })  

}
load_irrigation_queue_data()
})
     
     
     

      

  

  

