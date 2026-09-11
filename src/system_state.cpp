#include "system_state.h"
#include "rtos_objects.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"

static SystemState current_state = SystemState::ACTIVE;
static uint32_t last_motion_tick = 0;

SystemState evaluateSystemState(SystemState current,
                                bool motionDetected,
                                uint32_t elapsedSinceLastMotionMs,
                                uint32_t timeoutMs)
{
    if (current == SystemState::ACTIVE) {
        if (!motionDetected && elapsedSinceLastMotionMs >= timeoutMs) {
            return SystemState::INACTIVE;
        }
        return SystemState::ACTIVE;
    } else {
        if (motionDetected) {
            return SystemState::ACTIVE;
        }
        return SystemState::INACTIVE;
    }
}

void system_state_init(void)
{
    current_state = SystemState::ACTIVE;
    last_motion_tick = (uint32_t)xTaskGetTickCount();
    if (systemEventGroup != nullptr) {
        xEventGroupSetBits(systemEventGroup, EVENT_ACTIVE);
    }
}

SystemState get_current_system_state(void)
{
    return current_state;
}

void system_state_record_motion(void)
{
    last_motion_tick = (uint32_t)xTaskGetTickCount();
    if (current_state == SystemState::INACTIVE) {
        current_state = SystemState::ACTIVE;
        if (systemEventGroup != nullptr) {
            xEventGroupSetBits(systemEventGroup, EVENT_ACTIVE);
        }
        safe_log("STATE", "Motion detected: Transitioning to ACTIVE state");
    }
}

void state_task(void *pvParameters)
{
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(500));

        uint32_t now = (uint32_t)xTaskGetTickCount();
        uint32_t elapsed_ms = (now - last_motion_tick) * portTICK_PERIOD_MS;

        /* Check event group for active motion */
        EventBits_t bits = (systemEventGroup != nullptr) ?
                           xEventGroupGetBits(systemEventGroup) : 0;
        bool motion_active = (bits & EVENT_MOTION) != 0;

        SystemState next = evaluateSystemState(current_state, motion_active, elapsed_ms, INACTIVITY_TIMEOUT_MS);

        if (next != current_state) {
            current_state = next;
            if (current_state == SystemState::INACTIVE) {
                if (systemEventGroup != nullptr) {
                    xEventGroupClearBits(systemEventGroup, EVENT_ACTIVE);
                }
                safe_log("STATE", "Inactivity timeout (%u ms): Entering INACTIVE state (Power-Save)", (unsigned int)INACTIVITY_TIMEOUT_MS);
            } else {
                if (systemEventGroup != nullptr) {
                    xEventGroupSetBits(systemEventGroup, EVENT_ACTIVE);
                }
                safe_log("STATE", "System restored to ACTIVE state");
            }
        }
    }
}
