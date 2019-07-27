
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
   


    $( "#soil_type_id" ).change(  function(event, ui) 
    {   var soil_index
       
        local_data["soil_type_index"]  = $("#soil_type_id")[0].selectedIndex;
        
        calculate_data();
     });

    $( "#soil_depth_id" ).change(  function(event, ui) 
    {   var soil_depth_index
        
        local_data["soil_depth_index"] = $("#soil_depth_id")[0].selectedIndex;
        calculate_data();       
     });

    $( "#recharge_ratio_id" ).change(  function(event, ui) 
    {  
        
        local_data["recharge_ratio_index"]  = $("#recharge_ratio_id")[0].selectedIndex;
        calculate_data();         
     });

    $( "#sprayer_radius_id" ).change(  function(event, ui) 
    {   var sprayer_radius_id
        
        local_data["sprayer_radius_index"]  = $("#sprayer_radius_id")[0].selectedIndex;
        calculate_data();     
     }); 


    $( "#sprayer_rate_id" ).change(  function(event, ui) 
    {   var sprayer_rate_id
        
        local_data["sprayer_rate_index"]  = $("#sprayer_rate_id")[0].selectedIndex;
        calculate_data();         
     });

    $( "#sprayer_efficiency_id" ).change(  function(event, ui) 
    {   var sprayer_efficiency_id
        
        local_data[ "sprayer_efficiency_index"]  = $("#sprayer_efficiency_id")[0].selectedIndex;
        calculate_data();     
     });


    $( "#salt_flush_id" ).change(  function(event, ui) 
    {   var salt_flush_id
        
        local_data["salt_flush_index"]  = $("#salt_flush_id")[0].selectedIndex;
        calculate_data();         
     });

    $( "#crop_utilization_id" ).change(  function(event, ui) 
    {   
        
        local_data["crop_utilization_index"]  = $("#crop_utilization_id")[0].selectedIndex;
        calculate_data();         
     });

    $( "#edit_panel_save" ).click(  function(event, ui) 
    {   
        
         
 
       var json_data = {}
       var json_string;
       var url;
       var result = confirm("Do you want to change schedule data ?");
       if( result == true )
       {    // making update
             if( add_flag == true )
             {
               
                eto_data.push( local_data );
             }
             else
             {
                eto_data[ref_index] = local_data;
             }
             json_object = eto_data
             var json_string = JSON.stringify(json_object);
             url = window.location.href;
             $.ajax
             ({
                    type: "POST",
                    url: '/ajax/save_app_file/eto_site_setup.json',
                    dataType: 'json',
                    async: true,
                    contentType: "application/json",
                    data: json_string,
                    success: function () 
		    {
                       window.location.href = url;
  
                    },
                    error: function () 
		    {
                       alert('/ajax/save_app_file/eto_site_setup.json'+"  Server Error Change not made");

		      
		       
                    }
              })
      }

     });

    $( "#edit_panel_cancel" ).click(  function(event, ui) 
    {   
        $("#main_panel").show()
        $("#station_setup").hide()
                 
     });
    $( "#edit_panel_reset" ).click(  function(event, ui) 
    {   
          load_controls(ref_index);
       
     });


 
     function find_index()
     {
       var i;
     

       
       for( i=0; i< eto_data.length; i++)
       {
           if( $("#eto_emiter_id_"+i).is(':checked') == true )
           {
               return i;
           }
        }
       return  -1;  // no item selected
    
     
     }
     $("#action-choice-a").bind('change',function(event,ui)
     {
       var index
       

       if( $("#action-choice-a").val() == "edit" )
       {
            index = find_index()
            if( index >= 0 )
            {
                  load_controls(index)
                  $("#add_controls").hide()
                  $("#main_panel").hide()
                  $("#station_setup").show()
  
            }
            else
            {
                alert("No Eto Resource Selected")            
            }

       }
       if( $("#action-choice-a").val() == "delete" )
       {       
               index = find_index()
               if( index >= 0 )
               {
                  eto_data.splice(index, 1);
                  save_data();
               }
               else
               {
                alert("No Eto Resource Selected")            
                }

           
       }
       if( $("#action-choice-a").val() == "add" )
       {
            add_controls()
            $("#add_controls").show()
            $("#main_panel").hide()
            $("#station_setup").show()

       }
       $("#action-choice-a")[0].selectedIndex = 0;
       $("#action-choice-a").selectmenu('refresh');
     })

  $( "#valve_controllera" ).bind( "change", valve_panel_controller_select );
  $( "#valve_valvea").bind("change",valve_panel_valve_select );
  $("#main_panel").show();
  $("#station_setup").hide();
  function save_data()
  {   
        
         
 
       var json_data = {}
       var json_string;
       var url;
       var result = confirm("Do you want to change schedule data ?");
       if( result == true )
       {    
             json_object = eto_data
             var json_string = JSON.stringify(json_object);
             url = window.location.href;
             $.ajax
             ({
                    type: "POST",
                    url: '/ajax/save_app_file/eto_site_setup.json',
                    dataType: 'json',
                    async: true,
                    contentType: "application/json",
                    data: json_string,
                    success: function () 
		    {
                       window.location.href = url;
  
                    },
                    error: function () 
		    {
                       alert('/ajax/save_app_file/eto_site_setup.json'+"  Server Error Change not made");

		      
		       
                    }
              })
      }

     }
  });
