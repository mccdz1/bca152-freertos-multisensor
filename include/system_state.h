#pragma once

#include <stdint.h>
#include <stdbool.h>

#define INACTIVITY_TIMEOUT_MS 15000U // 15 seconds for rapid testing

enum class SystemState {
    ACTIVE,
    INACTIVE
};

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize system state management
 */
void system_state_init(void);

/**
 * @brief Get authoritative current system state
 */
SystemState get_current_system_state(void);

/**
 * @brief Record a motion event (resets inactivity timer and restores ACTIVE state)
 */
void system_state_record_motion(void);

/**
 * @brief FreeRTOS task managing state transitions and inactivity timeouts
 */
void state_task(void *pvParameters);

#ifdef __cplusplus
}
#endif

/**
 * @brief Pure, testable state machine transition function
 * @param current Current system state (ACTIVE or INACTIVE)
 * @param motionDetected Whether motion is actively detected
 * @param elapsedSinceLastMotionMs Milliseconds elapsed since last observed motion
 * @param timeoutMs Configured inactivity timeout threshold
 * @return Next SystemState
 */
SystemState evaluateSystemState(SystemState current,
                                bool motionDetected,
                                uint32_t elapsedSinceLastMotionMs,
                                uint32_t timeoutMs);
