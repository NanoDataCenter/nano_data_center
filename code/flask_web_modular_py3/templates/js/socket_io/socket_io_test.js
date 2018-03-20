$(document).ready(
 function()
 {
     
     


     function display_results(data)
     {
       
         $("#ping_result").val(data)

     } 
    
     
     function connect_function()
     {
          socket = io.connect('https://' + document.domain + ':' + location.port+"/test");
          socket.on( "ping_event", display_results) 
          socket.on( "message", display_results) 

     }
     
     function disconnect_function()
     {
       socket.disconnect()
     }
     
     function ping_function()
     {
 
        socket.emit("ping_event",$("#ping_input").val())
         
     }
 
     
     $("#connect_button").bind("click",connect_function )
     $("#disconnect_button").bind("click",disconnect_function)
     $("#ping_button").bind("click",ping_function )
     hostname = window.location.hostname
     pathname =  window.location.pathname
     url = "wss://"+hostname+"/"+"socket_test"  // websocket ttl
    
    
  
   
  

  
 });
