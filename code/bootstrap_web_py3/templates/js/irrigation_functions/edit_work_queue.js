
function refresh_data(event,ui)
{
       window.location.href = window.location.href
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
            
           
	         temp  = data[i];
          temp_index = i +1;    
	         html +=   '<label for=qid'+i+'  >Schedule '+temp.schedule_name+
                    "    Step: "+temp.step+"   Run Time "+temp.run_time +"</label>"
	         html +=   '<input type=checkbox   id=qid'+i+' />';
             
        }
        html += "</div>";
        
   } // else
      
     
   $("#queue_elements").append (html)

 
        
} 


function  delete_jobs(event,ui)
{
	 
   var status = [];
	  var update_flag = 0;
   for( i=0;i<jobs.length;i++)
	  {
	   
	     if( $("#schedule_list"+i).is(":checked") == true )
	     {
             
	         status.push(jobs.length-1-i);
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
  
  json_object["list_indexes"]         = status 
  ajax_post_confirmation('/ajax/irrigation_job_delete', json_object,"Do you want to delete jobs?",
                            "Changes Made", "Changes Not Made") 
 
  setTimeout(refresh_data,1000)

}

$(document).ready(
 function()
 {
 
   $("#refresh_b").bind("click",refresh_data)
   $("#delete_limits").bind("click",delete_jobs)

 }
)
     
     
     

      

  








