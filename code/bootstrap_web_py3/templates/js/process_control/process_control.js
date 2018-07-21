
function refresh_data(event,ui)
{
       
       load_data();
}  

function load_data()
{
   json_object = {}
   json_object["controller"]  = controller_id

  
   ajax_post_get('/manage_processes/load_process',json_object, getQueueEntries, "Initialization Error!!!!") 
}
function getQueueEntries(  )
{
   
   var html = ""; 
   $("#queue_elements").empty();
   
   for( i = 0; i < keys.length; i++ )
   {           
       if( eto_current_data[i] < 0 )
       { 
           eto_current_data[i] = 0.00 
       }
       temp_index = i +1;  
       id = "check"+i
       html += "<div>"
       data = '<label for=id'+i+"> "+keys[i]+"    ---   Water Deficient (inch) -->"+eto_current_data[i].toFixed(2) +"</label>"
      html += '<div class="btn-group" >'
      html += '<label class=class="btn  btn-toggle" for="check'+i+'">'
      html +=  '<input type="checkbox" class="btn  btn-toggle"  id="'+id+'"    name="option"   >'+data
               +'</label>'
      html += '</div>'
      html += '</div>'
    
             
   }
  
   $("#queue_elements").append (html)
     
 }
     

function getQueueEntries( data )
{
  
   var temp_index;
   var temp
   var html;

   data_ref = data
   $("#queue_elements").empty();
   
      
   if( display_list.length == 0 )
   {
      var html = "";
      html +=  "<h3>No Processes managed </h3>";
	  
	 
	 
   }
   else
   {
       var html = "";
       
	      html += '';

       for( i = 0; i < display_list.length; i++ )
       {
          temp_index = i +1;  
          id = "check"+i
          html += "<div>"
          
          name = display_list[i]
	      temp  = data_ref[name]
          data1 = 'Process: '+temp.name+" -- Enabled: "+temp.enabled+"  -- Active: "+
                    "    Active: "+temp.active+" --  Error State: "+temp.error 
          data = '<label for='+id+">"+data1+" </label>"
          html += '<div class="btn-group" >'
          html += '<label class=class="btn  btn-toggle" for="'+id+'">'
          html +=  '<input type="checkbox" class="btn  btn-toggle"  id="'+id+'"    name="option"   >'+data
               +'</label>'
          html += '</div>'
          html += '</div>'
           
             
           
        }
        html += "</div>";
        
   } // if
      
     
   $("#queue_elements").append (html)



   for( i = 0; i < display_list.length; i++ )
   {
       name = display_list[i]
	   temp  = data_ref[name]
       id = "#check"+i
       if(temp.enabled == True)
       {
           $(id).prop('checked', true)
       }
       else
       {
           $(id).prop('checked', false)
        }
	 
   }   
 

}
        



function  change_process_status(event,ui)
{
	 
	  
   for( i=0;i<display_list.length;i++)
   {
	                  
        name = display_list[i]
	    temp  = data_ref[name]
        id = "#check"+i
   
	     if( $(id).is(":checked") == true )
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
  json_object["controller"]  = controller_id
  json_object["process_data"] = temp_json
  ajax_post_confirmation('/manage_processes/change_process', json_object,"Do you want to start/kill selected processes ?",
                            "Changes Made", "Changes Not Made") 
  

}

$(document).ready(
 function()
 {
   load_data()   
   $("#refresh_b").bind("click",refresh_data)
   $("#change_state").bind("click",change_process_status)

 }
)
     
     
     

      


