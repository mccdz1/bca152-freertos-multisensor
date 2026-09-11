#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"

#define PIN_BUZZER GPIO_NUM_15

#define LOW_TEMPERATURE_LIMIT  18.0f
#define HIGH_TEMPERATURE_LIMIT 30.0f

enum class AlarmState {
    NORMAL,
    LOW_TEMPERATURE,
    HIGH_TEMPERATURE
};

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize buzzer GPIO output
 */
void alarm_init(void);

/**
 * @brief Set physical buzzer state
 */
void buzzer_set(bool state);

/**
 * @brief FreeRTOS Alarm management task (Priority 2)
 */
void alarm_task(void *pvParameters);

#ifdef __cplusplus
}
#endif

/**
 * @brief Pure, testable temperature alarm decision logic
 * @param temperature Temperature in degrees Celsius
 * @return AlarmState (LOW_TEMPERATURE < 18.0, HIGH_TEMPERATURE > 30.0, NORMAL [18.0..30.0])
 */
AlarmState evaluateTemperature(float temperature);
