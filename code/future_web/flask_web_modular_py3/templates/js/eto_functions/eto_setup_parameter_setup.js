parameter_class = ""
parameter_url = ""
function parameter_success_function( data )
{
  window.location.href = parameter_url
}
class Parameter_Setup 
{
   constructor( ) 
   {
     $("#parameter_div").hide()
   }       

  load_controls( self , main_panel)
  {
     parameter_class = self
     $("#parameter_save").bind('click',self.save)
     $("#parameter_cancel").bind('click',self.cancel)
     $("#parameter_reset").bind('click',self.special_reset)
     $("#parameter_field").on("slidestop", "#parameter_input", this.update_display) 
  }      
  open( default_object,reference_object,title)
  {
     var value;
     $("#parameter_title").html(title)
     $("#main_panel").hide()    
     $("#parameter_div").show()
     parameter_class.reference_object = reference_object
     parameter_class.default_object = default_object
     value = reference_object[default_object[0]]
     
     $("#parameter_input").val( value)
     parameter_class.set_slider_title(value)
     $( "#parameter_input" ).slider( "refresh" );
     parameter_class.ref_object = value
  }
  save()
  {
       var result = confirm("Do you wish to save data?");  
       if( result == true )
       {
          var index = parameter_class.default_object[0]
          var ref_value = parseFloat($("#parameter_input").val( ))
          parameter_class.reference_object[index] = ref_value
          eto_data.forEach(refresh_stations)



          parameter_url = window.location.href;
          ajax_post_get('/ajax/save_app_file/eto_site_setup.json', 
                    eto_data,parameter_success_function,"Server Error")      
       }


   }
   cancel()
   {
     $("#main_panel").show()    
     $("#parameter_div").hide()

   }

   set_slider_title( value)
   {
     $("#parameter_display").html( this.default_object[2]+value*this.default_object[3]
                                   +this.default_object[4])      
   }

   special_reset()
   {
      
      $("#parameter_input").val( parameter_class.ref_object)
      parameter_class.update_display()
      $( "#parameter_input" ).slider( "refresh" );


    
   }

  update_display (event) 
  {
    var value
    value = $("#parameter_input"  ).val()
    
    $("#parameter_display").html( parameter_class.default_object[2]+
                                 value*parameter_class.default_object[3]
                                   +parameter_class.default_object[4])      
  }
}

/*   
    ref_class_name = class_name
    ref_parent_panel = parent_panel

    $(ref_class_name.div_tag).show()
    ref_class_name.set_reset_value(ref_class_name.get_value())

    $(ref_class_name.input_tag).val(this.value)
    $(ref_class_name.display_tag ).html(ref_class_name.display_string  
           + $(ref_class_name.input_tag  ).val() )   
    $(parent_panel).hide()
 
    

  }

  set_reset_value(value)
  {
     this.reset_value = value
  }

  get_reset_value()
  {
    return this.reset_value
  }  


  set_value(value)
  {
     this.value = value
  }
  get_value()
  {
    return this.value
  }  
  close(event, ui)  
  {
    ref_class_name.reset(event,ui)
    $(ref_class_name.div_tag).hide()  
    $(ref_parent_panel).show()
  }
  save( event,ui)
  {
    ref_class_name.close(event,ui)
  }

  reset( event,ui)
  { 
    ref_class_name.set_value(ref_class_name.get_reset_value())
    $(ref_class_name.input_tag).val(ref_class_name.get_value())
    $(ref_class_name.display_tag ).html(ref_class_name.display_string  
           + ref_class_name.get_value())  
    $(ref_class_name.input_tag ).slider("refresh")
    
  }


}  

*/