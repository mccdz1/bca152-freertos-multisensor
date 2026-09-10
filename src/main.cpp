#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

#include "rtos_objects.h"
#include "sensors.h"
#include "alarm.h"
#include "display.h"
#include "input.h"
#include "motion.h"
#include "system_state.h"

static const char *TAG = "MAIN";

/* Forward declaration of unit test runner from test suite */
extern "C" int run_all_unit_tests(void);

extern "C" void app_main(void)
{
    /* Step 9: Required startup diagnostic logging */
    ESP_LOGI(TAG, "BCA152 FreeRTOS Multisensor");
    ESP_LOGI(TAG, "System starting...");

    /* Execute automated unit test suite (Part XIV - 13 Unit Tests) */
    ESP_LOGI(TAG, "Executing built-in automated unit test suite...");
    run_all_unit_tests();

    /* 1. Hardware and Primitive Initialization */
    rtos_objects_init();
    sensors_init();
    alarm_init();
    input_init();
    motion_init();
    system_state_init();
    display_init();

    safe_log("MAIN", "All hardware drivers and RTOS synchronization primitives initialized");

    /* 2. FreeRTOS Task Creation with Explicit Priorities */
    /* MotionTask: Priority 3 (High urgency - immediate PIR event detection) */
    xTaskCreate(motion_task, "MotionTask", 3072, nullptr, 3, nullptr);

    /* InputTask: Priority 3 (High urgency - responsive rotary encoder UI interaction) */
    xTaskCreate(input_task, "InputTask", 3072, nullptr, 3, nullptr);

    /* SensorTask: Priority 2 (Periodic 2-second telemetry with vTaskDelayUntil) */
    xTaskCreate(sensor_task, "SensorTask", 4096, nullptr, 2, nullptr);

    /* AlarmTask: Priority 2 (Timely reaction to anomalous temperature readings) */
    xTaskCreate(alarm_task, "AlarmTask", 3072, nullptr, 2, nullptr);

    /* StateTask: Priority 2 (Authoritative system power/inactivity state machine) */
    xTaskCreate(state_task, "StateTask", 3072, nullptr, 2, nullptr);

    /* DisplayTask: Priority 1 (Background visual refresh - lowest priority) */
    xTaskCreate(display_task, "DisplayTask", 4096, nullptr, 1, nullptr);

    safe_log("MAIN", "All 6 FreeRTOS tasks spawned. Scheduler taking over.");

    /* app_main returns cleanly; FreeRTOS scheduler runs all tasks */
}
