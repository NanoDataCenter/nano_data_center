
/*
        <option selected value=0>No Action</option>
	        <option value=1>Zero Selected ETO Data</option>
	        <option value=2>Subtract .01 inch from ETO Data</option>
	        <option value=3>Add .01 inch to ETO Data</option>
	        <option value=4>Subtract .05 inch from ETO Data</option>
	        <option value=5>Add .05 inch to ETO Data</option>
	        <option value=6>Select All Elements</option>
	        <option value=7>Unselect All Elememts</option>
	        <option value=8>Reload Data</option>
	        <option value=9>Save ETO Data</option>    
*/
function load_data() 
{
   
   json_object = "ETO_RESOURCE"
   ajax_post_get("/ajax/redis_hgetall", json_object, getQueueEntries, "Init Data Error!!!") 
}
     
function save_data()
{
       var temp;
       var json_object;
       var json_string;
       var i;
            
       
       temp = {}
       json_object = []
       for( i = 0; i < keys.length; i++ )
       {
           temp = { "redis_key": "ETO_RESOURCE","hash":keys[i],"value":eto_current_data[i] }
               
           json_object.push(temp)
       }
       
	      uncheck_elements()
	      save_check_state();
   
       ajax_post_confirmation("/ajax/redis_hset", json_object, "Do you want to change eto values", 
                                       "Changes Made", "Server Error changes not made" )
}
      
 
function getQueueEntries( data )
{
   var i;
   var temp;       
   eto_current_data = []
   eto_ref_data     = []
     
   $("#eto_list").empty();
   keys = Object.keys(data)  
   keys.sort()    
   if( keys.length == 0 )
   {
       var html = "";
       html +=  "<h3>No ETO Setups</h3>";
   }
   else
   {
       for( i= 0; i< keys.length; i++)
       {
           temp = parseFloat(data[keys[i]]);
           eto_current_data.push( temp );
           eto_ref_data.push(temp)
       }
	      display_data();
	      uncheck_elements()
       save_check_state();

	  }
}

function save_check_state()
{
   check_status = [];
   for( i=0;i<eto_current_data.length;i++)
	  {
	   
	     if( $("#id"+i).is(":checked") == true )
	     {       
	         check_status.push(1);
	         update_flag = 1;
	     }
	     else
	     {
	         check_status.push(0);
	     }
	 }
}


function process_end_results()
{
  switch( $("#eto_op_mode")[0].selectedIndex )
  {
	     case 6:    
	         check_elements();
	         save_check_state();
		        break;
	     case 7:  
	        uncheck_elements()
	        save_check_state();
	        break;
         case 8: 
            
            load_data()
            break;	
	     case 9: save_data()
            break;
   }
   display_data( eto_current_data );  
}
    
function process_data(i)
{
     
   switch( $("#eto_op_mode")[0].selectedIndex )
   {
       case 0: 
           break;
       case 1:   
           eto_current_data[i] = 0.;
           break;
       case 2:
           eto_current_data[i] = eto_current_data[i] -.01; 
		         break;
       case 3:
           eto_current_data[i] = eto_current_data[i] +.01;   
           break;

       case 4:
           eto_current_data[i] = eto_current_data[i] -.05;
           break;
		
	      case 5:
           eto_current_data[i] = eto_current_data[i] +.05;   
           break;
 
	 
   }
       
}

       
function process_action(event,ui)
{
       
   save_check_state()
   for( i= 0; i<eto_current_data.length; i++ )
   {
             
       if( $("#id"+i).is(":checked") == true )
	      {     
	         process_data(i);  
	      }
	      else
	      {
	         ; // do nothing
	      }       
   }
       
   process_end_results();
   restore_check_state();
       
   $("#eto_op_mode")[0].selectedIndex = 0 
      
 }


function check_elements()
{
        
   for( i=0;i<eto_current_data.length;i++)
	  {
	     $("#id"+i).prop('checked', true).checkboxradio('refresh');
   }    
}

function uncheck_elements()
{        
  for( i=0;i<eto_current_data.length;i++)
	 {
	     $("#id"+i).prop('checked', false).checkboxradio('refresh');
	  
	 }     
}

function restore_check_state()
{
   for( i=0;i<eto_current_data.length;i++)
	  {
	     if( check_status[i] |= 0 )
	     {
	         $("#id"+i).prop('checked', true).checkboxradio('refresh');
	     }
	     else
	     {
	         $("#id"+i).prop('checked', false).checkboxradio('refresh');
	      }
	  
	   }
}

function display_data(  )
{
   var html = ""; 
   $("#eto_list").empty();
   for( i = 0; i < keys.length; i++ )
   {           
       if( eto_current_data[i] < 0 )
       { 
           eto_current_data[i] = 0.00 
       }
       temp_index = i +1;    
	      html +=   '<label for=id'+i+"> "+keys[i]+"    ---   Water Deficient (inch) -->"+eto_current_data[i].toFixed(2) +"</label>"
	      html +=   '<input type=checkbox   id=id'+i+' />';
             
   }
   html += "</div>";
   $("#eto_list").append (html)
   for( i = 0; i < keys.length; i++ )
   {
       $("#id"+i).checkboxradio();
       $("#id"+i).checkboxradio("refresh");	 
   }     
 }
     
 
     
 
     
     
     
     
  
$(document).ready(
 function()
 {  
  
       
   $("#eto_op_mode").bind('change',process_action)
   load_data();
 }


)
