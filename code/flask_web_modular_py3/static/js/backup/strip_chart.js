$(document).ready(

 
 
  function()
  {  var g,h,i
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
     path = $("#ajax_command").attr('path')
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
                            valueRange: [ limit_low,limit_high ],
                            labels: [x_axis, y_axis]
                          });
     
     
   
     var strip_chart_update = function(data)
     {
         
	hh.updateOptions( { 'file': data } );

      }



     var ajax_success = function(temp)
     {
       var temp
       var temp_1
       var tempDate
       
       tempDate = new Date()
       
       data = temp.queue
       temp = data;
       temp_2 = [];
       var t = new Date();
       
       for ( i = 0; i < temp.length ; i++)
       {
        var x = new Date(t.getTime() - (temp.length - i) * 60000);
        temp_2.push([x,Number(temp[i]) ]);
       }
       
       strip_chart_update( temp_2 )
       if( notify == true )
       {
           alert("changes made")
       }
    

     }
  
     
   
     var ajax_request = function()
     {
       
           
            $.ajax
            ({
                    type:               "POST",
                    url:                path,
                    dataType:           'json',
                    async:              true,
                    success:            ajax_success,
                    error: function () 
		    {
		      
                       alert( "/ajax/strip_chart/"+path+"  Server Error Request Not Successful");
		   
		       
                    }
              })
	  
     }
 
   
   

     


     
     notify = false
     ajax_request();
     notify = true
     $("#refresh").bind("click",function(event,ui)
     {
 
       ajax_request();
     });
     

  

  } )

