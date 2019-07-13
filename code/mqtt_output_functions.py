
 mqtt_ctrl_register_subscription("OUTPUTS/GPIO/SET", app_ouput_set_pin_data );
   return CF_DISABLE;      
} 
   
 mqtt_ctrl_register_subscription("INPUT/GPIO/READ", app_input_read_cb );
 
 
 
 
  mqtt_ctrl_register_subscription("INPUT/MQTT_CURRENT/GET_LIMIT_CURRENTS", get_limit_currents );
    mqtt_ctrl_register_subscription("INPUT/MQTT_CURRENT/GET_MAX_CURRENTS", get_max_currents );
    mqtt_ctrl_register_subscription("INPUT/MQTT_CURRENT/CLEAR_MAX_CURRENTS", clear_max_currents );
    mqtt_ctrl_register_subscription("INPUT/MQTT_CURRENT/READ_CURRENT", read_currents );
    mqtt_ctrl_register_subscription("OUTPUT/MQTT_CURRENT/ENABLE_EQUIPMENT_RELAY", enable_equipment_relay );
    mqtt_ctrl_register_subscription("OUTPUT/MQTT_CURRENT/ENABLE_IRRIGATION_RELAY", enable_irrigation_relay );
    mqtt_ctrl_register_subscription("OUTPUT/MQTT_CURRENT/DISABLE_EQUIPMENT_RELAY", disable_equipment_relay );
    mqtt_ctrl_register_subscription("OUTPUT/MQTT_CURRENT/DISABLE_IRRIGATION_RELAY", disable_irrigation_relay );
    mqtt_ctrl_register_subscription("OUTPUT/MQTT_CURRENT/READ_RELAY_STATES", read_relay_states );
    
    
     mqtt_ctrl_register_subscription("OUTPUTS/PWM/CHANGE_DUTY", app_pwm_change_duty );
       mqtt_ctrl_register_subscription("OUTPUTS/PWM/REQUEST_DUTY", app_pwm_read_duty );
           gpio_message.write_gpio_pins([25,26,27],[1,1,1])
    time.sleep(5)
    gpio_message.write_gpio_pins([25,26,27],[0,0,0])
    time.sleep(2)