#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_DHT22 GPIO_NUM_4
#define PIN_LDR   GPIO_NUM_34

/**
 * @brief Canonical sensor data structure required by laboratory specification
 */
struct SensorData {
    float temperature;    /**< Temperature in degrees Celsius */
    float humidity;       /**< Relative humidity in percent */
    int   lightLevel;     /**< Ambient light level in 0-100% */
    bool  motionDetected; /**< Current PIR motion detection flag */
};

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize sensor hardware (GPIO and ADC)
 */
void sensors_init(void);

/**
 * @brief Read current DHT22 temperature and humidity
 * @param[out] temp Temperature in Celsius
 * @param[out] hum Relative humidity in percent
 * @return true on valid read, false on checksum/timeout error
 */
bool dht22_read(float *temp, float *hum);

/**
 * @brief Read ambient light level from LDR through ADC
 * @return Scaled light level (0 - 100%)
 */
int ldr_read_light_level(void);

/**
 * @brief FreeRTOS Sensor acquisition task
 * Runs periodically every 2000 ms using vTaskDelayUntil()
 */
void sensor_task(void *pvParameters);

#ifdef __cplusplus
}
#endif
