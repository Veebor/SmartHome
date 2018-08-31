//#include <PubSubClient.h>

#include "ESP8266WiFi.h"
#include <ESP8266WebServer.h>
#include "./DNSServer.h"
#include "MQTT.h"

const char* mqtt_server = "clfbv.cf";
const char* user= "NodeMCU";
const char* password= "SmartHome";
char* ssid;
char* passw;
IPAddress    apIP(10, 10, 10, 1);

WiFiClient espClient;
MQTTClient client;
//Creating server...
ESP8266WebServer server(80);
DNSServer        dnsServer;
String responseHTML = "<!DOCTYPE html><html><head><title>Sensor 1</title></head><body>"
                      "<h1>Welcome to SmartHome!</h1><p>Insert your SSID and password"
                      "here to configure this sensor.</p>"
                      "<form action='http://10.10.10.1/submit' method='POST'>"
                      "SSID:<br><input type='text' name='ssid' value='SSID'><br>"
                      "Password:<br><input type='text' name='password' value='password'><br><br>"
                      "<input type='submit' value='Submit'></body></html>"
                      "</form>";

long lastMsg = 0;
char msg[50];
int value = 0;
int temp = 22;

void handleRoot() {
  server.send(200, "text/plain", responseHTML);
}

int handleSubmit() {
  if (server.args() > 0 ) {
    for ( uint8_t i = 0; i < server.args(); i++ ) {
      if (server.argName(i) == "ssid") {
        String ssidx = server.arg(i);
        Serial.println(ssidx);
        char ssid[ssidx.length()];
        ssidx.toCharArray(ssid, ssidx.length());
      }
      else if (server.argName(i) == "password") {
        String passwx = server.arg(i);
        Serial.println(passwx);
        char passw[passwx.length()];
        passwx.toCharArray(passw, passwx.length());
        return 1;
      }
    }
  }
}

void WiFiuserpass() {
  Serial.print("Setting soft-AP ... ");
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  boolean result = WiFi.softAP("Sensor 1", "smarthome");
  if(result == true)
  {
    Serial.println("Ready");
  }
  else
  {
    Serial.println("Failed!");
  }
  server.on("/", handleRoot);
  server.on("/submit", handleSubmit);
  //Redirect all requests to our IP
  dnsServer.start(53, "*", apIP);
  //Start server
  server.begin();
  server.onNotFound([]() {
    server.send(200, "text/html", responseHTML);
  });
  Serial.println("Server Started");
  while(1) {
    dnsServer.processNextRequest();
    server.handleClient();
    if(handleSubmit() == 1) {
      WiFi.softAPdisconnect(true);
      break;
    }
  }


}

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, passw);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  // Switch on the LED if an 1 was received as first character
  if ((char)payload[0] == '1') {
    digitalWrite(D4, HIGH);
  } else {
    digitalWrite(D4, LOW);
  }

}

void mqttconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(), user, password)) {
      Serial.println("Connected");
      // Once connected, publish an announcement...
      client.publish("TempSens", "Connected!", 0, 2);
      // ... and resubscribe
      client.subscribe("ToSens", 2);
    } else {
      Serial.print("failed...");
      //Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  pinMode(D4, OUTPUT);     // Initialize the D4 pin as an output
  Serial.begin(115200);
  WiFiuserpass();
  setup_wifi();
  client.begin(mqtt_server, espClient);
  client.onMessage(callback);
  mqttconnect();
}

void loop() {
  if (!client.connected()) {
    mqttconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 10000) {
     lastMsg = now;
     snprintf (msg, 75, "Temperature = %ld", temp);
     Serial.print("Publish message: ");
     Serial.println(msg);
     client.publish("TempSens", msg, 0, 2);
   }
}
