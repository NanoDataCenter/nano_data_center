
function refresh_data(event,ui)
{
       
       load_data();
}  

function load_data()
{
   json_obj = [process_data_key]
   
   ajax_post_get('/ajax/redis_get',json_obj, getQueueEntries, "Initialization Error!!!!") 
}


function getQueueEntries( data )
{
  
   var temp_index;
   var temp
   var html;
   
   data = data[process_data_key]
   data_ref = JSON.parse(data)
   

   
   $("#queue_elements").empty();
   
      
   if( display_list.length == 0 )
   {
      var html = "";
      html +=  "<h3>No Processes managed </h3>";
	  
	 
	 
   }
   else
   {
       var html = "";
       
	      html += '<div data-role="controlgroup">';

       for( i = 0; i < display_list.length; i++ )
       {
           
             
             name = display_list[i]
	         temp  = data_ref[name]
             temp_index = i +1; 
             html += "<div id=div"+i+' />'
	         html +=   '<label for=qid'+i+'  >Process: '+temp.name+" -- Enabled: "+temp.enabled+"  -- Active: "+
                    "    Active: "+temp.active+" --  Error State: "+temp.error +"</label>"
	         html +=   '<input  type=checkbox   id=qid'+i+' />';
             html += "</div>"
        }
        html += "</div>";
        
   } // if
      
     
   $("#queue_elements").append (html)



   for( i = 0; i < display_list.length; i++ )
   {
       name = display_list[i]
	   temp  = data_ref[name]
       $("#qid"+i).checkboxradio();
       $("#qid"+i).checkboxradio("refresh");
       if(temp.enabled == True)
       {
           $("#qid"+i).prop('checked', true).checkboxradio('refresh');
       }
       else
       {
           $("#qid"+i).prop('checked', true).checkboxradio('refresh');
        }
	 
   }   
 

}
        



function  change_process_status(event,ui)
{
	 
   
	  
   for( i=0;i<display_list.length;i++)
   {
	                  
        name = display_list[i]
	    temp  = data_ref[name]
   
	     if( $("#qid"+i).is(":checked") == true )
	     {
	         data_ref[name].enabled = true
	     }
	     else
	     {
	        
	        data_ref[name].enabled = false
	     }
     
  }
  let temp_json = JSON.stringify(data_ref)
  json_object = {}
  json_object[command_queue_key] = temp_json
  ajax_post_confirmation('/ajax/redis_lpush', json_object,"Do you want to start/kill selected processes ?",
                            "Changes Made", "Changes Not Made") 
  //setTimeout(load_data,1000)

}

$(document).ready(
 function()
 {
   load_data()   
   $("#refresh_b").bind("click",refresh_data)
   $("#change_state").bind("click",change_process_status)

 }
)
     
     
     

      
/*


   for( i = 0; i < display_list.length; i++ )
   {
     let  name = display_list[i]
	 let  temp  = data_ref[name]
     
     if( temp.error == true)
     {
         alert("should not happen")
        $("#qid"+i).css('background-color', 'red');
        $("#qid"+i).css('color', 'white');
        $("#qid"+i).checkboxradio("refresh");       
         
     }
     else if( temp.enabled == true )
     {    
        alert(i)
        $("#div"+i).css({'background-color': 'green'})
        $("#div"+i).css({'color': 'yellow'})
        
          
     }
     else
     {  alert("should not happen")
        $("#qid"+i).css('background-color', 'yellow');
        $("#qid"+i).css('color', 'black');
        $("#qid"+i).checkboxradio("refresh");    
     }
     
      
  }
*/
  








