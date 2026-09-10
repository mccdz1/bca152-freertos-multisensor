#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"
#include "input.h"
#include "sensors.h"

#define PIN_OLED_SDA GPIO_NUM_21
#define PIN_OLED_SCL GPIO_NUM_22
#define OLED_I2C_ADDR 0x3C

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize I2C master and SSD1306 OLED display
 */
void display_init(void);

/**
 * @brief FreeRTOS Display management task (Priority 1)
 * Sole owner of the OLED display hardware.
 */
void display_task(void *pvParameters);

/**
 * @brief Update latest sensor data cache for display rendering
 */
void display_update_sensor_data(const SensorData *data);

/**
 * @brief Turn display screen on or off (used by power management state machine)
 */
void display_set_power(bool on);

#ifdef __cplusplus
}
#endif
