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
     

 
         var hh = new Dygraph(document.getElementById("div_g"), data,
                          {
                           width  : $(window).width(),
                            height : $(window).height()*.65,

                            drawPoints: true,
                            showRoller: true,
                            valueRange: [-.5, 1.0 ],
                            labels: ['Time', 'Current']
                          });
     
     
   
     var strip_chart_update = function(data)
     {
            
	hh.updateOptions( { 'file': data } );

      }



     var ajax_success = function(data)
     {
       var temp
       var temp_1
       var tempDate
       
       tempDate = new Date()
       
 

       temp = data;
       temp_2 = [];
       var t = new Date();
       for ( i = 0; i < temp.length ; i++)
       {
        var x = new Date(t.getTime() - (temp.length -i) * 60000);
        temp_2.push([x,Number(temp[i]) ]);
       }

       strip_chart_update( temp_2 )
    
       

     }

     var ajax_request = function()
     {
       
     
            $.ajax
            ({
                    type: "GET",
                    url: '/ajax/get_recent_plc',
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    data: [],
                    success: ajax_success,
                    error: function () 
		    {
		      
                       alert('/ajax/get_recent_plc'+"  Server Error Request Not Successful");
		   
		       
                    }
              })
	  
     }
 
    

     


     
     // get flow sensors
     ajax_request();
     $("#back").button();
     $("#refresh").bind("click",function(event,ui)
     {
 
       ajax_request();
     });

  

  } )

