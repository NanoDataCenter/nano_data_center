
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
	  
	 
	 
   }
   else
   {
       var html = "";
       html +=  "<h3>Selects select elements to be deleted from queue </h3>";
	      html += '<div data-role="controlgroup">';

       for( i = 0; i < data.length; i++ )
       {
            
           
	         temp  = JSON.parse(data[i]);
          temp_index = i +1;    
	         html +=   '<label for=qid'+i+'  >Schedule '+temp.schedule_name+
                    "    Step: "+temp.step+"   Run Time "+temp.run_time +"</label>"
	         html +=   '<input type=checkbox   id=qid'+i+' />';
             
        }
        html += "</div>";
        
   } // else
      
     
   $("#queue_elements").append (html)

   for( i = 0; i < data.length; i++ )
   {
        $("#qid"+i).checkboxradio();
        $("#qid"+i).checkboxradio("refresh");	 
   }
        
} 


function  delete_jobs(event,ui)
{
	 
   var status = [];
	  var update_flag = 0;
   for( i=0;i<queue_values.length;i++)
	  {
	   
	     if( $("#qid"+i).is(":checked") == true )
	     {
	         status.push(queue_values.length-1-i);
	         update_flag = 1;
	     }
	     else
	     {
	        
	        ;
	     }
     
	 }
  if( update_flag == 0 )
  { 
      set_status_bar("no changes selected"); 
      return; 
  }
  status.reverse()  
  json_object = {}
  json_object["key"]     = "QUEUES:SPRINKLER:IRRIGATION_QUEUE"
  json_object["list_indexes"]         = status 
  ajax_post_confirmation('/ajax/redis_ldelete', json_object,"Do you want to delete jobs?",
                            "Changes Made", "Changes Not Made") 
  setTimeout(load_data,500)

}

$(document).ready(
 function()
 {
   load_data()   
   $("#refresh_b").bind("click",refresh_data)
   $("#delete_limits").bind("click",delete_jobs)

 }
)
     
     
     

      

  








