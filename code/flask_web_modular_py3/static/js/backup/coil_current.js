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
                            valueRange: [0, 20.0 ],
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
        var x = new Date(t.getTime() - (temp.length - i) * 60000);
        temp_2.push([x,Number(temp[i]) ]);
       }
       
       strip_chart_update( temp_2 )
       if( notify == true )
       {
           alert("changes made")
       }
    

     }
     
     path = $("#ajax_command").attr('path')
     var ajax_request = function()
     {
       
     
            $.ajax
            ({
                    type:          "GET",
                    url:           path,
                    dataType:      'json',
                    async:         false,
                    data:          [],
                    success:      ajax_success,
                    error: function () 
		    {
		      
                       alert( path+"  Server Error Request Not Successful");
		   
		       
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

