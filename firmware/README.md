# User Manual
## Introduction
This user manual provides instructions for using the **VMBook** to capture and upload photos. The guide includes steps for setup, usage, and important considerations.

## Hardware Components
- **ESP32S3 Sense:** The primary microcontroller board with an integrated camera.
- **Type-C Data Cable:** For connecting the ESP32S3 Sense to your computer.

## Setup Instructions
- Connect the ESP32S3 Sense board to your computer using the USB cable.
- Install the required libraries: esp_camera, WiFi, HTTPClient, SPIFFS, Base64, and ArduinoJson.
- Upload the provided Arduino code to the ESP32S3 Sense board.


## Usage Steps
1. Power on the ESP32S3 Sense board. Ensure it is properly connected to your computer or power source.
2. Connect to Wi-Fi: The board will automatically connect to the predefined Wi-Fi network.
3. Select Mode and Capture Photos:
   - **Automatic Mode:** Press Button 1 (RESET) and Button 2 (GPIO 1) to start. The board will capture and upload a photo every 5 seconds automatically. Press Button 1 again to stop, this will lead the board to Deep Sleep Mode.
    - **Manual Mode:** Press Button 1 (RESET) to start. The board will capture a photo, upload it to the server, and then enter Deep Sleep mode to save power.

## Highlights
- **Dual Mode Operation:** Automatic Mode allows continuous monitoring, ensuring no detail is missed; while Manual Mode provides more customization and greater flexibility, with extended battery life.
- **Automatic Retransmission:** Whether due to network issues or server failures, if the photo fails to upload, it will automatically retry, ensuring that precious memories are not lost. During retransmission, an orange light will illuminate, prompting the user to check the network and server status.

## Upload Confirmation
- Ensure the Wi-Fi credentials are correctly set in the code.
- The default capture interval is set to 5 seconds; adjust this as needed in the code.
- The server URL for uploading photos is predefined; ensure the server is running and accessible.

## TODO
- [ ] Add additional button to control power in Battery-powered mode.
- [ ] Add user voice input functionality so that users can enhance images with background and emotional descriptions.