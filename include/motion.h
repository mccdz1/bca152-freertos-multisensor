#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"

#define PIN_PIR GPIO_NUM_13

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize PIR sensor GPIO
 */
void motion_init(void);

/**
 * @brief FreeRTOS Motion monitoring task (Priority 3)
 */
void motion_task(void *pvParameters);

/**
 * @brief Read current PIR sensor level directly
 */
bool motion_read_current(void);

#ifdef __cplusplus
}
#endif
