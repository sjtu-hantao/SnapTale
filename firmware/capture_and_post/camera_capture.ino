#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <SPIFFS.h>
#include "Base64.h"
#include <ArduinoJson.h>
#include "Arduino.h"
#include "img_converters.h"

#define CAMERA_MODEL_XIAO_ESP32S3 // Has PSRAM

#include "camera_pins.h"

const char *ssid = "DSO-2.4G";
const char *password = "dso12345";
const char *user_id = "894fe364-fabc-404f-b9ba-36fd2a63f510";
const char *device_id = "first_test_machine";
// const String serverUrl1 = String("http://192.168.0.34:8000/users/") + user_id + "/photos";
const String serverUrl1 = String("http://test:8000/uploadfile/") ;  // For test
const String serverUrl2 = String("http://test:8000/photos/");

const int buttonPin1 = 1; // 假设按钮连接到GPIO 1
const int buttonPin2 = 7; // 假设按钮连接到GPIO 7
const int buttonPinWakeUp = 6;
bool isManualMode = true; // 默认模式为手动模式

unsigned long lastCaptureTime = 0;
const unsigned long captureInterval = 5000;  // Capture every 5 sec

void print_wakeup_reason() {
  esp_sleep_wakeup_cause_t wakeup_reason;

  wakeup_reason = esp_sleep_get_wakeup_cause();

  switch(wakeup_reason) {
    case ESP_SLEEP_WAKEUP_EXT0 : Serial.println("Wakeup caused by external signal using RTC_IO"); break;
    case ESP_SLEEP_WAKEUP_EXT1 : Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case ESP_SLEEP_WAKEUP_TIMER : Serial.println("Wakeup caused by timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD : Serial.println("Wakeup caused by touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP : Serial.println("Wakeup caused by ULP program"); break;
    default : Serial.printf("Wakeup was not caused by deep sleep: %d\n", wakeup_reason); break;
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial);

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  pinMode(buttonPin1, INPUT_PULLUP);
  pinMode(buttonPin2, INPUT_PULLUP);

  Serial.println("Starting setup...");

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
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
      Serial.println("PSRAM found, setting higher quality and frame buffer count");
    } else {
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
      Serial.println("PSRAM not found, limiting frame size");
    }
  } else {
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
    // Serial.println("Configured for face detection/recognition");
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }

  Serial.println("Camera initialized successfully");
  sensor_t *s = esp_camera_sensor_get();
  s->set_whitebal(s, 1);  // 设置白平衡
  s->set_awb_gain(s, 0);  // 自动白平衡增益
  s->set_wb_mode(s, 2);   // 白平衡模式 0: Auto, 1: Sunny, 2: Cloudy, 3: Office, 4: Home


  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  lastCaptureTime = millis();
}

void loop() {
  unsigned long now = millis();
  // Test by change the condition which determines whether a button is pressed
  // The initial states of the buttons are HIGH 
  bool buttonState = digitalRead(buttonPin1) == HIGH; 
  bool buttonCap = digitalRead(buttonPin2) == HIGH;

  if (buttonState) {
    takeAndSendPhoto();
    // Mode selection
    Serial.println("Going to sleep now");
    esp_deep_sleep_start();
    Serial.println("This will never be printed");
  } else {
    if ((now - lastCaptureTime) >= captureInterval) {
      takeAndSendPhoto();
      lastCaptureTime = now;
    }
  }
}

void takeAndSendPhoto() {
  for (int i = 0; i < 3; ++i) {
    Serial.println("Taking a photo...");
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Failed to get camera frame buffer");
      return;
    }
    // String encoded ="data:image/jpeg;base64," + base64::encode(fb->buf, fb->len);
    String encoded =String(fb->buf);
    // String encoded = convertToBase64(fb);
    Serial.println("Binary Image:");
    Serial.println( encoded);
    // Serial.write((const uint8_t*)&len, sizeof(len));
    // Serial.write(fb->buf, fb->len);
    esp_camera_fb_return(fb);

    if (httpPost(encoded)){
      Serial.println("Picture uploading successes!");
      return;
    }else if (i<2){
      Serial.println("Photo uploading failed, will automatically re-take the photo when the orange light goes out");
      digitalWrite(LED_BUILTIN, LOW);
      delay(1000);
      digitalWrite(LED_BUILTIN, HIGH);
    }else{
      Serial.println("Picture uploading failes for 3 times, please try at another time.");
    }
  }
}

bool httpPost(String binaryImage) {
  HTTPClient http;
  http.begin(serverUrl1);
  http.addHeader("Content-Type", "application/json");

  // 构建JSON数据
  DynamicJsonDocument doc(200);  // 200是JSON文档的大小，可以根据需要调整
  doc["image"] = binaryImage;   // 将传入的Base64编码的图像数据添加到JSON对象中
  doc["user_id"] = user_id;
  doc["device_id"] = device_id;
  doc["location"] = WiFi.localIP();
  doc["description"] = "a cup";
  // 可以添加更多字段到JSON对象中...

  // 序列化JSON数据为字符串
  String jsonStr;
  serializeJson(doc, jsonStr);
  Serial.println("Post body, in json string format:");
  Serial.println(jsonStr);

  // 发送POST请求
  int httpResponseCode = http.POST(jsonStr);

  // int httpResponseCode = http.POST(fileBuffer, fileSize);

  String jstring_response = http.getString();
  String photo_id = checkResponse(jstring_response);
  if (photo_id != ""){
    Serial.println("Key 'photo_id' exists with value: ");
    Serial.println(photo_id);

  }
  else{
    Serial.println("Error on sending POST: ");
    Serial.println(httpResponseCode);
    Serial.println("Error response:");
    Serial.println(jstring_response);
    return false;
  }

  http.end();
  // Analysis

  // 创建第二个HTTPClient对象，发送第二个请求（不需要等待响应）
  HTTPClient http2;
  http2.begin(serverUrl2 + photo_id + "/analyze");  // 替换为第二个请求的目标URL
  http2.GET();
  delay(1000);
  http2.end();
  return true;
  
}

String checkResponse (String jsonString) {
  // 创建一个StaticJsonDocument对象（根据实际的JSON大小调整容量）
  StaticJsonDocument<200> doc;

  // 解析JSON字符串
  DeserializationError error = deserializeJson(doc, jsonString);

  // 检查解析是否成功
  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    return "";
  }

  // 检查是否存在特定键
  if (doc.containsKey("photo_id")) {
    const char* value = doc["photo_id"];
    return String(value);
  } else {
    return "";
  }
}

// Function to convert framebuffer to JPEG and then encode to base64
String convertToBase64(camera_fb_t *fb) {
  if (!fb) {
    Serial.println("Failed to get camera frame buffer");
    return "";
  }

  uint8_t *jpg_buf = nullptr;
  size_t jpg_len = 0;

  if (!frame2jpg(fb, 80, &jpg_buf, &jpg_len)) {
    Serial.println("Failed to convert frame buffer to JPEG");
    return "";
  }

  String encoded = "data:image/jpeg;base64," + base64::encode(jpg_buf, jpg_len);
  
  // Free the JPEG buffer
  free(jpg_buf);

  return encoded;
}