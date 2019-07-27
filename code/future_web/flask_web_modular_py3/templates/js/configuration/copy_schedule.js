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



function check_duplicate( new_schedule )
{   var i;  
    for( i = 0; i < schedule_list.length; i++ )
    {
       if( schedule_list[i] == new_schedule )
       {
           return false;
       }
    }
    return true;
}  

function copy_schedule_data( new_schedule )
{
         var status;
         var copy_schedule
         status = check_radio_selection()
         if( status[0] == true )
         {
           copy_schedule            = status[1]
           
           working_data            = temp_data
           working_data["link"]    = new_schedule+".json"
           working_data["name"]    = new_schedule
           schedule_data[new_schedule] = working_data
           return_value = true;
      
        } 
        else
        {
           return_value = false
        }

       return return_value;

}


function copy_schedule(event, ui) 
{
       
   new_schedule = $("#new_schedule" ).val()
   if( new_schedule.length == 0 )
   {
       set_status_bar("need to input new_schedule")
       return
   }
   if(  check_duplicate( new_schedule ) == true ) 
   {
       edit_schedule = new_schedule
       if( copy_schedule_data( new_schedule ) == true )
       {      
              confirmation_string = "Do you want to add "+new_schedule
              make_change_update( new_schedule, schedule_data ,confirmation_string)
              location.reload()
       
       }
       else
       {
          set_status_bar("no copy schedule selected")
       }
   }
  else
  {
          set_status_bar("duplicate schedule "+ $("#new_schedule" ).val())
   }
}




$(document).ready(
 function()
 {
    

 $( "#action_button" ).bind( "click", copy_schedule );

 
     

 }
)
