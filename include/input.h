#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"

#define PIN_ENCODER_CLK GPIO_NUM_18
#define PIN_ENCODER_DT  GPIO_NUM_19
#define PIN_ENCODER_SW  GPIO_NUM_5

enum class DisplayMode {
    TEMPERATURE,
    HUMIDITY,
    LIGHT,
    MOTION
};

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize rotary encoder GPIOs with pull-ups
 */
void input_init(void);

/**
 * @brief Get currently selected display mode
 */
DisplayMode input_get_display_mode(void);

/**
 * @brief FreeRTOS Input Task (Priority 3) for processing rotary encoder
 */
void input_task(void *pvParameters);

#ifdef __cplusplus
}
#endif

/**
 * @brief Pure navigation logic: Clockwise transition with wraparound
 */
DisplayMode nextDisplayMode(DisplayMode current);

/**
 * @brief Pure navigation logic: Counter-clockwise transition with wraparound
 */
DisplayMode previousDisplayMode(DisplayMode current);
