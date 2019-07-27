

$(document).ready(
 function()
 {
    
   function load_new_schedule_data()
   {
      working_data = {} 
      working_data["description"]      = ""
      working_data["step_number"]      = 0
      working_data["start_time"]       = [0, 0]
      working_data["link"]             = edit_schedule+".json"
      working_data["end_time"]         = [0, 0]
      working_data["controller_pins"]  = []
      working_data["steps"]   = []
      working_data["dow"]     = [0, 0, 0, 0, 0, 0, 0], 
      working_data["name"]    = edit_schedule
   }

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

   function copy_schedule_data( new_schedule )
   {
         var status;
         var copy_schedule
         status = check_radio_selection()
         if( status[0] == true )
         {
           copy_schedule            = status[1]
           schedule_data           = JSON.parse(JSON.stringify( schedule_data))
           working_data            = schedule_data[copy_schedule]
           working_data["link"]    = new_schedule+".json"
           working_data["name"]    = new_schedule
           return_value = true;
        } 
        else
        {
           return_value = false
        }

       return return_value;

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

   function assemble_page()
   {
     
     var new_schedule
     var action_button = {}
     
     add_function = function(event, ui) 
     {
       new_schedule = $("#new_schedule" ).val()
       if( check_duplicate( new_schedule ) )
       {
    
          edit_schedule = new_schedule
          load_new_schedule_data( new_schedule )
          load_controls( working_data )
          $("#define-schedule").hide()
          
          show_start_panel()
       }
       else
       {
          alert("duplicate schedule "+ $("#new_schedule" ).val())
       }
     }

     copy_function = function(event, ui) 
     {
       new_schedule = $("#new_schedule" ).val()
       if( check_duplicate( new_schedule ) )
       {
          edit_schedule = new_schedule
          
          if( copy_schedule_data( new_schedule ) == true )
          {
              set_schedule_name( new_schedule )
              load_controls( working_data )
              $("#define-schedule").hide()
              show_start_panel()          
          }
          else
          {
             alert("no schedule selected")
          }
       }
       else
       {
          alert("duplicate schedule "+ $("#new_schedule" ).val())
       }
     }
   
     edit_function = function(event, ui) 
     {
          var temp;
          temp = check_radio_selection()
          if( temp[0] == true )
          {   
              
              set_schedule_name( temp[1] )
              
              working_data  = JSON.parse(JSON.stringify( schedule_data[temp[1]]))
              
              load_controls( working_data )
              
              $("#define-schedule").hide()
              show_start_panel()          
          }
          else
          {
             alert("no schedule selected")
          }
       }

     delete_function = function(event, ui) 
     {
          var temp;
          temp = check_radio_selection()
          if( temp[0] == true )
          {   
             
              make_change("delete",temp[1])          
          }
          else
          {
             alert("no schedule selected")
          }
       }     
   if( template_type =="edit")
   {
      
      $( "#action_button" ).bind( "click", edit_function );
   }


   if( template_type =="add")
   {
      
      $( "#action_button" ).bind( "click", add_function );
   }
   if( template_type =="copy")
   {
      
      $( "#action_button" ).bind( "click", copy_function );
   }
   if( template_type == "delete")
   {

     $( "#action_button" ).bind( "click", delete_function );
   }

  }
   


 
     


 
 

  
  assemble_page();
  assem_page = assemble_page
  initialize_edit_functions();
  initialize_edit_panel();
  initialize_start_panel();
  initialize_edit_a_step_panel();
  initialize_edit_a_valve_panel();
  $("#edit_panel").hide();
 }
)
