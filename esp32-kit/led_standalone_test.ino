/**
 * Exploration Robotics Internship - DJI RoboMaster TT (Tello Talent)
 * Standalone Top RGB LED Hardware Test using official RMTT_Libs
 */

#include "RMTT_Libs.h"
#include "RMTT_RGB.h"

void setup() {
    Serial.begin(115200);
    Serial.println("[RMTT SETUP] Initializing RoboMaster TT Hardware...");

    // Initialize the top RGB LED hardware interface via RMTT_Libs
    RMTT_RGB::Init();

    Serial.println("[RMTT SETUP] RMTT_RGB Interface Ready.");
}

void loop() {
    // --- 1. Red ---
    Serial.println("[RGB TEST] RED");
    RMTT_RGB::SetRGB(255, 0, 0);
    delay(1000);

    // --- 2. Green ---
    Serial.println("[RGB TEST] GREEN");
    RMTT_RGB::SetRGB(0, 255, 0);
    delay(1000);

    // --- 3. Blue ---
    Serial.println("[RGB TEST] BLUE");
    RMTT_RGB::SetRGB(0, 0, 255);
    delay(1000);

    // --- 4. Yellow ---
    Serial.println("[RGB TEST] YELLOW");
    RMTT_RGB::SetRGB(255, 255, 0);
    delay(1000);

    // --- 5. Cyan ---
    Serial.println("[RGB TEST] CYAN");
    RMTT_RGB::SetRGB(0, 255, 255);
    delay(1000);

    // --- 6. Purple ---
    Serial.println("[RGB TEST] PURPLE");
    RMTT_RGB::SetRGB(128, 0, 128);
    delay(1000);

    // --- 7. LED Off / Blink Pulse ---
    Serial.println("[RGB TEST] OFF");
    RMTT_RGB::SetRGB(0, 0, 0);
    delay(500);
}