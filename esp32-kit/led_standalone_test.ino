/**
 * Exploration Robotics Internship - DJI RoboMaster TT (Tello Talent)
 * Top RGB LED Modes Test (Solid, Blink, Breath) using official RMTT_Libs
 */

#include "RMTT_Libs.h"
#include "RMTT_RGB.h"

void setup() {
    Serial.begin(115200);
    Serial.println("[RMTT SETUP] Initializing RoboMaster TT Hardware...");

    // Initialize the top RGB LED hardware interface
    RMTT_RGB::Init();

    Serial.println("[RMTT SETUP] RMTT_RGB Interface Ready.");
}

void loop() {
    // ==========================================
    // 1. SOLID COLOR MODE
    // ==========================================
    Serial.println("[RGB MODE] Solid RED");
    RMTT_RGB::SetRGB(255, 0, 0); // (R, G, B)
    delay(2000);

    Serial.println("[RGB MODE] Solid BLUE");
    RMTT_RGB::SetRGB(0, 0, 255);
    delay(2000);

    // ==========================================
    // 2. BLINK MODE
    // Syntax: Blink(r, g, b, freq_hz)
    // ==========================================
    Serial.println("[RGB MODE] Blinking GREEN (2 Hz)");
    RMTT_RGB::Blink(0, 255, 0, 2.0);
    delay(4000);

    Serial.println("[RGB MODE] Blinking YELLOW Fast (5 Hz)");
    RMTT_RGB::Blink(255, 255, 0, 5.0);
    delay(4000);

    // ==========================================
    // 3. BREATH / FADE MODE
    // Syntax: Breath(r, g, b, freq_hz)
    // ==========================================
    Serial.println("[RGB MODE] Breathing CYAN (1 Hz)");
    RMTT_RGB::Breath(0, 255, 255, 1.0);
    delay(5000);

    Serial.println("[RGB MODE] Breathing PURPLE (0.5 Hz)");
    RMTT_RGB::Breath(128, 0, 128, 0.5);
    delay(5000);

    // ==========================================
    // 4. RESET / OFF
    // ==========================================
    Serial.println("[RGB MODE] Turning LED Off");
    RMTT_RGB::SetRGB(0, 0, 0);
    delay(1000);
}