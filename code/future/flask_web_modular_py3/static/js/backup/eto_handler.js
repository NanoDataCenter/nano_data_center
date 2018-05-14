
/*
	    <option selected value=0>Zero Selected ETO Data</option>
	    <option value=1>Subtract .05 inch from ETO Data</option>
	    <option value=2>Add .05 inch from ETO Data</option>
	    <option value=3>Select All Elements</option>
	    <option value=4>Unselect All Elememts</option>
*/

$(document).ready(
 function()
 {  
  
     var result;
     var json_object;
     var json_string;
     var eto_ref_data;
     var eto_current_data;    // data of eto 
     var keys;                // keys of eto data
     var check_status;

     function save_data()
     {
       var temp;
       var json_object;
       var json_string;
       var i;
      
 
            
       json_object = {}
       json_object["hash_name"] ="ETO_RESOURCE"
       temp = {}
       for( i = 0; i < keys.length; i++ )
       {
           temp[ keys[i] ] = eto_current_data[i];
       }
       json_object["key_list"] = temp
       json_string = JSON.stringify(json_object);
   
       
       
       var result = confirm("Do you want to change eto");
       if( result == true )
       {    // making update
	    uncheck_elements()
	    save_check_state();
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/set_redis_hkeys',
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    data: json_string,
	            contentType: "application/json",
                    success: function () 
		    {
                       alert("Changes Made");
		       load_data()
		       
                    },
                   error: function () 
		    {
                       alert('/ajax/set_redis_hkeys '+"Server Error Change not made");
		      
		       
                    }

              });
        }
               
       
       
       
       
       
       
       
     }

     $("#eto_op_mode").bind('change',function(event,ui)
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
      
     });
     
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

		
	 case 8: 
	        
	        eto_current_data[i] = eto_ref_data[i];
		break;
	 
       }
       
   }
   
function display_data(  )
     {
           var html = "";
	   
	   $("#eto_list").empty();
            for( i = 0; i < keys.length; i++ )
            {
              
	      if( eto_current_data[i] < 0 ){ eto_current_data[i] = 0.00 }
  
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
     
     
     
     function uncheck_elements()
     {
        
         for( i=0;i<eto_current_data.length;i++)
	 {
	     $("#id"+i).prop('checked', false).checkboxradio('refresh');
	  
	 }

       
     }
     
     function check_elements()
     {
        
         for( i=0;i<eto_current_data.length;i++)
	 {
	    $("#id"+i).prop('checked', true).checkboxradio('refresh');
	  
	 }

       
     }
     
     function getQueueEntries( data )
     {
         var i;
         var temp;       
         eto_current_data = []
         eto_ref_data     = []
         
         $("#eto_list").empty();
         keys = Object.keys(data)      
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
      
   function load_data(event, ui) 
   {
     
 
     
      json_object = {}
      json_object["hash_name"] = "ETO_RESOURCE"
      var json_string = JSON.stringify(json_object);
      
       
      $.ajax
      ({
	
                    type: "POST",
                    url: '/ajax/get_redis_all_hkeys',
                    dataType: 'json',
                    async: true,
                    data: json_string,
                    success: getQueueEntries, 
                    contentType: "application/json",
		   
                    error: function () 
		    {
                       alert('/ajax/get_redis_all_hkeys'+"  Server Error Change not made");
		   
		       
                    }
      })
          
	
   }
  
   $("#refresh_c").bind("click",function(event,ui)
   {
     
      load_data();
      
   });
   load_data();
 }


)
