parameter_url = ""
function parameter_success_function( data )
{
  window.location.href = parameter_url
}

var station_control_class = ""
class Station_Setup 
{
   constructor(  )
   {
     $("#station_setup_set").hide()
   }

   load_controls( self )
   {
     station_control_class = self     
     $("#station_save").bind('click',self.save_control)
     $("#station_cancel").bind('click',self.cancel_control)
     $("#station_reset").bind('click',self.reset_control)
     $("#station_radius_field").on("slidestop", "#station_tree_radius", self.tree_radius_change) 
     $("#station_rate_field").on("slidestop", "#station_sprayer_rate", self.sprayer_rate_change) 
     $("#station_controller").bind('change',self.controller_change)
     $("#station_valve").bind("change",self.valve_change)
   }

   open( index, add_flag, eto_data , main_panel)
   {
      station_control_class.main_panel = main_panel
      station_control_class.add_flag = add_flag
      station_control_class.eto_data = eto_data
      station_control_class.index    = index
      $(main_panel).hide()
      $("#station_setup_set").show()
       if( add_flag == true )
       {
           $("#station_add_controls").show()
           station_control_class.populate_controllers()
           station_control_class.populate_valves()
           if( eto_data.length == 0 )
           {    
               station_control_class.reference_data = { }
               station_control_class.reference_data["recharge_eto"] =  .07
               station_control_class.reference_data["crop_utilization"] =      .8
               station_control_class.reference_data["sprayer_effiency"] =     .8
               station_control_class.reference_data["salt_flush_addition"] =   .1 
               station_control_class.reference_data["tree_radius"] = 6
               station_control_class.reference_data["sprayer_rate"] = 14.5;
               station_control_class.reference_data["controller"] 
                                       = $("#station_controller").val()
               station_control_class.reference_data["pin"] = $("#station_valve").val()
               station_control_class.backup_data 
                     = deepCopyObject(station_control_class.reference_data)


           }
           else
           {
               station_control_class.reference_data 
                     = deepCopyObject(station_control_class.eto_data[0])

               station_control_class.reference_data["pin"] = $("#station_valve").val()
               station_control_class.backup_data 
                     = deepCopyObject(station_control_class.reference_data)

               station_control_class.backup_data 
                     = deepCopyObject(station_control_class.reference_data)


           }
       

      }
      else
      {
         $("#station_add_controls").hide()
         station_control_class.reference_data = deepCopyObject(eto_data[index])
         station_control_class.backup_data = deepCopyObject(eto_data[index])

      }
      station_control_class.reset_control()
   }


   save_control()
   {
       var result = confirm("Do you wish to save data?");  
       if( result == true )
       {
          if( station_control_class.add_flag == false)
          {   
              var index = station_control_class.index
              station_control_class.eto_data[index] = station_control_class.reference_data          
          }
          else
          {    eto_data.push(station_control_class.reference_data)
               
          }

          parameter_url = window.location.href;
          //alert(JSON.stringify(station_control_class.eto_data[index]))

          ajax_post_get('/ajax/save_app_file/eto_site_setup.json', 
                    eto_data,parameter_success_function,"Server Error")      
       }


   }
   reset_control()
   {
     //alert(JSON.stringify(station_control_class.reference_data))
     station_control_class.reference_data["tree_radius"] = 
         station_control_class.backup_data["tree_radius"]

     var tree_radius = station_control_class.reference_data["tree_radius"]
     $("#station_tree_radius").val( tree_radius)
     station_control_class.set_tree_radius_title(tree_radius)
     $( "#station_tree_radius" ).slider( "refresh" );
     
     station_control_class.reference_data["sprayer_rate"] = 
         station_control_class.backup_data["sprayer_rate"]

     var sprayer_rate = station_control_class.reference_data["sprayer_rate"]
     $("#station_sprayer_rate").val( sprayer_rate)
     station_control_class.set_sprayer_capacity(sprayer_rate)
     $( "#station_sprayer_rate" ).slider( "refresh" );
     station_control_class.calculate_recharge_rate()   

 

   }
   
   cancel_control()
   {
      $(main_panel).show()
      $("#station_setup_set").hide()
     
   }

   controller_change()
   {
      
      station_control_class.populate_valves()
      station_control_class.reference_data["controller"] = $("#station_controller").val()

   }

   valve_change()
   {
      var index = $("#station_valve").val()

      var value = station_control_class.controller_values[$("#station_controller").val()][index -1] 

      station_control_class.reference_data["pin"] = value
   }

   tree_radius_change(value)
   {
       var value = $("#station_tree_radius").val()
       station_control_class.reference_data["tree_radius"] = value
       station_control_class.set_tree_radius_title( value)
       station_control_class.calculate_recharge_rate()
   }

   sprayer_rate_change()
   {
       var value = $("#station_sprayer_rate").val()
      station_control_class.reference_data["sprayer_rate"] = value

       station_control_class.set_sprayer_capacity( value)
      station_control_class.calculate_recharge_rate()
   }

   set_sprayer_capacity(value )
   {
     

     $("#station_sprayer_rate_display").html("Sprayer Rate (Gallons/Hour)  " +value)      
   }

   set_tree_radius_title( value )
   {
     

     $("#station_radius_display").html("Tree Radius (feet)  " +value)      
   }

   set_eto_display( value)
   {
      $("#station_eto_display").html("Current ETO Recharge Rate (in/hr) is : "+value+" </h3>")  
   }

   calculate_recharge_rate()
   {
       var item = station_control_class.reference_data
       var value = station_control_class.calculate_eto_data( item["sprayer_rate"],
                                                             item["tree_radius"] ,
                                                             item["sprayer_effiency"],
                                                             item["salt_flush_addition"],  
                                                             item["crop_utilization"])       
       station_control_class.set_eto_display( value)
       station_control_class.reference_data["recharge_rate"] = value

   }

   calculate_eto_data( sprayer_rate,
                         tree_radius,
                         sprinkler_efficiency,
                         salt_flush,
                         crop_utilization )

   {
        // effective volume is ft3/hr
        // sprayer rate is in Gallons/hr
        // 1 gallon is 0.133681 ft3
        //console.log(sprayer_rate)
        //console.log(tree_radius)
        //console.log(sprinkler_efficiency)
        //console.log(salt_flush)
        //console.log(crop_utilization)
        
        effective_rate = sprayer_rate*sprinkler_efficiency/crop_utilization/(1+salt_flush)
        effective_volume = 0.133681 * effective_rate
        effective_area =  tree_radius*tree_radius*3.14159
        return (effective_volume/effective_area)*12; // converting the eto to inches
   }

   populate_controllers(  )
   { 
       this.structure_data() 
 
       $("#station_controller").empty() 
       for(let  i= 0; i< this.controller_list.length; i++)
       {
          $("#station_controller").append($("<option></option>").val(this.controller_list[i]).html(this.controller_list[i]));
       }
       $("#station_controller").selectmenu("refresh");
   }

   populate_valves()
   {
        var controller_index;

        controller_index = $("#station_controller")[0].selectedIndex;
        var select_pins = this.controller_labels[this.controller_list[controller_index]]
    
        $("#station_valve").empty()
        for( let i = 0; i < select_pins.length; i++)
        {      
          $("#station_valve").append($("<option></option>").val(i+1).html(select_pins[i]));
        } 
   
    
       $("#station_valve").selectmenu("refresh")
   }

   structure_data(  )
   { 
       var i;
       var temp_value;
       var name;
       var length;
    
       var temp_value; 
       var j;
       var valve_location;

     
       var controller_labels = {}
       var controller_list   = []
       var controller_values = {}
       for( let i=0; i<pin_list.length; i++ )
       {
           name   = pin_list[i]["name"]
           length = pin_list[i]["pins"].length;
         
           controller_labels[name] = []
           controller_list.push(name)
           controller_values[name] = []
       
           for( let j = 0; j < length; j++)
           {
            
               temp_value = pin_list[i]["pins"][j];

              if( this.match_step_valve(j,name) == true )
              {
               
                   ; //controller_labels[name].push("I/O:  "+j+ "    ----- Defined in Irrigation Step Donot Select  ");
               }

               else
               {
                   controller_labels[name].push("I/O:  "+(j+1)+ "    Description : "+temp_value);
                   controller_values[name].push(j+1)
              
               }

           }

      }
      this.controller_labels = controller_labels
      this.controller_list   = controller_list
      this.controller_values = controller_values

    }

    match_step_valve( index, controller )
    {
       // this is a very inefficent way of doing this
       // but rarely executed function and eto_data is not large
       for( let i = 0; i < this.eto_data.length; i++ )
       {
           if( ( this.eto_data[i]["controller"] == controller ) && 
               ( this.eto_data[i]["pin"] == (index +1) ) )
          {
          
             return true; 
          }
       } 
       return false;
   }

} 



