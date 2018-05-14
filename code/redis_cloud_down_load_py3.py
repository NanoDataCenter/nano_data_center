


import paho.mqtt.client as mqtt
import ssl

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
#client.username_pw_set("remote1", "ready2go")
#client.username_pw_set("remote","AbpUkwsU9s3jJy7B")
client.username_pw_set("cloud","v3GZP8prWPJnJYNM")
#client.tls_set_context(ssl.create_default_context())
client.tls_set(ca_certs=None, certfile= "./device001.crt", keyfile= "./device001.key",cert_reqs=ssl.CERT_NONE ) #,cert_reqs=ssl.CERT_NONE )

print("starting to connect")    
client.connect("lacimaRanch.cloudapp.net", 8883, 60)
client.loop_forever(timeout=1.0, max_packets=1, retry_first_connection=False)
