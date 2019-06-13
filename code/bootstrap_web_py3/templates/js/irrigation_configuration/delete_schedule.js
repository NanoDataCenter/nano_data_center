function check_radio_selection()
{  
   var update_flag;
   var item;
   var schedule;

   return_value = [false,null]
   for( i = 0; i < schedule_list.length; i++ )
   {
       item = "#"+schedule_list[i]
       if( $(item).is(":checked") == true )
	      {
           return_value = [ true, schedule_list[i] ]
       }
   }
   return return_value	              

}




delete_function = function(event, ui) 
{
   var temp;
   temp = check_radio_selection()
   if( temp[0] == true )
   {   
          delete_schedule = temp[1]
          make_change_delete( delete_schedule, schedule_data )
          

       
   }
   else
   {
             set_status_bar("no schedule selected")
   }
}     



$(document).ready(
 function()
 {
    

 $( "#action_button" ).bind( "click", delete_function );

 
     

 }
)
