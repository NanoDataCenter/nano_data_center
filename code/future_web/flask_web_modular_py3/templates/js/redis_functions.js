/*
**
**
** File: redis_functions.js
**
**
**
*/



/*
**
**  Hash Functions
**
*/

function redis_hget( hash_name, key_list , success_function, error_failure_message)
{
            
   json_object = {}
   json_object["hash_name"] = hash_name;
   json_object["key_list"]  = key_list;
   ajax_post_get("/ajax/redis_hget", json_object, success_function, error_message) 
}

function redis_hgetall( hash_name, success_function, error_failure_message)
{
   ajax_post_get("/ajax/redis_hgetall", hash_name, success_function, error_message) 
}