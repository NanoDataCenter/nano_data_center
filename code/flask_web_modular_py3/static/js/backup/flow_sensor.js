




 
 
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
     
      

         var hh = new Dygraph(document.getElementById("div_g"), data,
                          {
                            width  : $(window).width(),
                            height : $(window).height()*.65,
                            drawPoints: true,
                            showRoller: true,
                            valueRange: [0, 40 ],
                            labels: ['Time', 'GPM']
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
       
       
       var data_object = ref_flow_meter;
       data_string = JSON.stringify( data_object );
       $.ajax
       ({
                    type: "GET",
                    url: '/ajax/get_flow_queue_data',
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    data: data_string,
                    success: ajax_success,
                    error: function () 
		    {
		      
                       alert('/ajax/get_flow_queue_data'+"  Server Error Request Not Successful");
		   
		       
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
          ref_flow_meter = 1;
	  conversion_factor_array = []

          for( i= 0; i < length; i++ )
          {
	    
            flow_meter.append('<option value='+(i+1)+'>'+data[i][0]+'</option>');
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
                    url: '/ajax/flow_sensor_names',
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    data: [],
                    success: flow_sensor_success,
                    error: function () 
		    {
		      
                       alert('/ajax/flow_sensor_names'+"  Server Error Request Not Successful");
		   
		       
                    }
              })
	  
     }
     

     flow_sensor_request();
     $("#back").button();
     $("#refresh").bind("click",function(event,ui)
     {

       ajax_request();
     });
  })
  



