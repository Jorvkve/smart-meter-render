#include <WiFi.h>
#include "esp_camera.h"
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

/* ================= WIFI ================= */
const char* ssid = "thxrd";
const char* password = "thxrd123.";

/* ======== RENDER SERVER ======== */
const char* serverUrl =
"https://smart-meter-render.onrender.com/upload";

/* ================= LED ================= */
#define RED_LED 33

void setLED(bool state){
  digitalWrite(RED_LED, state ? LOW : HIGH);
}

/* ============ CAMERA PIN (AI THINKER) ============ */
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

/* ================= CAMERA ================= */
void setupCamera(){

  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  camera_config_t config;

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;

  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;

  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;

  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;

  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  /* ⭐ เพิ่มคุณภาพภาพ */
  config.frame_size = FRAMESIZE_XGA;   // 1024x768
  config.jpeg_quality = 10;            // ชัดขึ้น
  config.fb_count = 2;

  if(esp_camera_init(&config) != ESP_OK){
    Serial.println("Camera Init Failed");
    ESP.restart();
  }

  sensor_t *s = esp_camera_sensor_get();

  /* ⭐ Optimize สำหรับอ่านเลข */
  s->set_brightness(s, 1);
  s->set_contrast(s, 2);
  s->set_saturation(s, -1);
  s->set_sharpness(s, 2);
  s->set_denoise(s, 1);
  s->set_gainceiling(s, GAINCEILING_8X);

  Serial.println("Camera Ready (AI MODE) ✅");
}

/* ================= WIFI ================= */
void connectWiFi(){

  WiFi.begin(ssid,password);

  Serial.print("Connecting WiFi");

  while(WiFi.status()!=WL_CONNECTED){
    Serial.print(".");
    setLED(true);
    delay(200);
    setLED(false);
    delay(200);
  }

  Serial.println("\nWiFi Connected ✅");
  Serial.println(WiFi.localIP());

  setLED(true);
}

/* ================= UPLOAD ================= */
void sendPhoto(){

  if(WiFi.status()!=WL_CONNECTED){
    connectWiFi();
    return;
  }

  camera_fb_t *fb = esp_camera_fb_get();

  if(!fb){
    Serial.println("Capture failed");
    return;
  }

  Serial.printf("Image Size: %d bytes\n", fb->len);

  WiFiClientSecure client;
  client.setInsecure();

  HTTPClient http;
  http.begin(client, serverUrl);

  String boundary="----ESP32CAM";

  http.addHeader(
    "Content-Type",
    "multipart/form-data; boundary="+boundary
  );

  String head =
  "--"+boundary+"\r\n"
  "Content-Disposition: form-data; name=\"image\"; filename=\"meter.jpg\"\r\n"
  "Content-Type: image/jpeg\r\n\r\n";

  String tail="\r\n--"+boundary+"--\r\n";

  int totalLen=head.length()+fb->len+tail.length();

  uint8_t *payload=(uint8_t*)malloc(totalLen);

  if(!payload){
    Serial.println("Memory alloc failed");
    esp_camera_fb_return(fb);
    return;
  }

  memcpy(payload,head.c_str(),head.length());
  memcpy(payload+head.length(),fb->buf,fb->len);
  memcpy(payload+head.length()+fb->len,
  tail.c_str(),tail.length());

  Serial.println("Uploading...");

  int httpCode=http.POST(payload,totalLen);

  Serial.printf("HTTP Code: %d\n",httpCode);

  if(httpCode==200){
    Serial.println("Upload Success ✅");
  }else{
    Serial.println("Upload Failed ❌");
  }

  free(payload);
  http.end();
  esp_camera_fb_return(fb);
}

/* ================= TIMER ================= */
unsigned long previousMillis = 0;
const unsigned long interval = 15000; // ⭐ 15 วินาที

/* ================= SETUP ================= */
void setup(){

  Serial.begin(115200);

  pinMode(RED_LED,OUTPUT);
  setLED(false);

  setupCamera();
  connectWiFi();
}

/* ================= LOOP ================= */
void loop(){

  unsigned long now = millis();

  if(now - previousMillis >= interval){
    previousMillis = now;
    sendPhoto();
  }
}