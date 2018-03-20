




 
 
$(document).ready(
 function()
 {  
    
     var ref_flow_meter;
     var conversion_factor_array;
     var conversion_factor_index;
     var conversion_factor;
     var g,h,i
     var alarm_data;
     var  queue_interval_id;
     var  nintervalId;
     var data = [];
     var t = new Date();
     for (var i = 100; i >= 0 ; i--)
     {
        var x = new Date(t.getTime() - i * 60000);
        data.push([x,0]);
     }
     
      path      = $("#ajax_command").attr('path')
     sel_function = $("#ajax_command").attr('sel_function')
     limit_low = $("#ajax_command").attr('limit_low')
     limit_high = $("#ajax_command").attr('limit_high')
     x_axis = $("#ajax_command").attr('x_axis')
     y_axis = $("#ajax_command").attr('y_axis')
     

         var hh = new Dygraph(document.getElementById("div_g"), data,
                          {
                            width  : $(window).width()*.9,
                            height : $(window).height()*.65,
                            drawPoints: true,
                            showRoller: true,
                            valueRange: [limit_low, limit_high ],
                            labels: [x_axis, y_axis]
                          });
     
     
     var strip_chart_update = function(data)
     {
        
	hh.updateOptions( { 'file': data } );

      }

     $("#flow_meter" ).bind( "change", function(event, ui)
     {

       ref_flow_meter = $("#flow_meter")[0].selectedIndex  +1;
       conversion_factor_index = $("#flow_meter")[0].selectedIndex;
       
       conversion_factor = conversion_factor_array[ conversion_factor_index ];
       
       ajax_request();
     });
     

     var ajax_success = function(data)
     {
       var temp
       var temp_1
       var tempDate
       
       
       tempDate = new Date()
       if( notify == true )
       {
             alert("Results Updated")
       }
       
 
       
       temp = data;
       temp_2 = [];
       var t = new Date();


       for ( i = 0; i < data.length ; i++)
       {
        var x = new Date(t.getTime() - (data.length -i) * 60000);
        temp_2.push([x,Number(temp[i])*conversion_factor ]);
       }

       strip_chart_update( temp_2 )

       

     }

     var ajax_request = function()
     {
       var data_object;
       var data_string;

       
   

       data_string = JSON.stringify( data_object );
       $.ajax
       ({
                    type: "POST",
                    url:  path+ref_flow_meter,
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    data: [],
                    success: ajax_success,
                    error: function () 
		    {
		      
                       alert(path+ref_flow_meter+"  Server Error Request Not Successful");
		   
		       
                    }
        })
	  
     }
 
    
   
     
     function flow_sensor_success( data )
     {
          var length;
          var i;
	  var flow_meter
	  flow_meter = $("#flow_meter");
          length = data.length;
          flow_meter.empty()
          ref_flow_meter = data[0][0]
	  conversion_factor_array = []
   
          for( i= 0; i < length; i++ )
          {
	    
            flow_meter.append('<option value='+(i+1)+'>'+"flow sensor  --->   "+data[i][0]+'</option>');
	    conversion_factor_array.push(data[i][1])
          }
         
          conversion_factor_index = 0;
	  conversion_factor = conversion_factor_array[ conversion_factor_index ];

          flow_meter.selectedIndex = 0;
	  flow_meter.selectmenu();
          flow_meter.selectmenu("refresh");
          ajax_request();
       
       
     }
     

    var flow_sensor_request = function()
     {
      
            
            $.ajax
            ({
                    type: "GET",
                    url: sel_function,
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    data: [],
                    success: flow_sensor_success,
                    error: function () 
		    {
		      
                       alert( sel_function+"  Server Error Request Not Successful");
		   
		       
                    }
              })
	  
     }
     
     notify = false
     flow_sensor_request();
     notify = true
     $("#back").button();
     $("#refresh").bind("click",function(event,ui)
     {

       ajax_request();
     });
  })
  



