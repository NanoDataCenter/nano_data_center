


function refresh_data(event,ui)
{
       load_data();
}  

function load_data()
{
   json_obj = {}
   json_obj["key"] = "QUEUES:SPRINKLER:IRRIGATION_QUEUE"
   json_obj["start"] = 0
   json_obj["end"]   = -1
   ajax_post_get('/ajax/redis_lrange',json_obj, getQueueEntries, "Initialization Error!!!!") 
}


function getQueueEntries( data )
{
       
   data.reverse()
   queue_values = data
   $("#queue_elements").empty();
   if( data.length == 0 )
   {
        var html = "";
        html +=  "<h3>No Elements in Work Queue </h3>";
	       //html += '<div data-role="controlgroup">'; 
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
	          html +=   '<li>  Schedule '+temp.schedule_name+
                   "    Step: "+temp.step+"   Run Time: "+temp.run_time +"</li>"
                   
             
       }
       html += "</ol>";
    } // else
      

    $("#queue_elements").append (html)

         
} 






$(document).ready(
 function()
 {
   load_data()   
   $("#refresh_c").bind("click",refresh_data)

 }
)
     
     
     

      

  

  

