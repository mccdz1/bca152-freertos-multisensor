#include "sensors.h"
#include "rtos_objects.h"
#include "motion.h"
#include "display.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_rom_sys.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static adc_oneshot_unit_handle_t adc1_handle = nullptr;
static float last_valid_temp = 24.5f;
static float last_valid_hum = 60.0f;

void sensors_init(void)
{
    /* Initialize DHT22 GPIO with pullup */
    gpio_config_t dht_conf = {};
    dht_conf.intr_type = GPIO_INTR_DISABLE;
    dht_conf.mode = GPIO_MODE_INPUT_OUTPUT_OD; // Open drain with pull-up
    dht_conf.pin_bit_mask = (1ULL << PIN_DHT22);
    dht_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    dht_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    gpio_config(&dht_conf);
    gpio_set_level(PIN_DHT22, 1);

    /* Initialize ADC1 for LDR on GPIO 34 (ADC_CHANNEL_6) */
    adc_oneshot_unit_init_cfg_t init_config = {};
    init_config.unit_id = ADC_UNIT_1;
    if (adc_oneshot_new_unit(&init_config, &adc1_handle) == ESP_OK) {
        adc_oneshot_chan_cfg_t chan_config = {};
        chan_config.atten = ADC_ATTEN_DB_12;
        chan_config.bitwidth = ADC_BITWIDTH_DEFAULT;
        adc_oneshot_config_channel(adc1_handle, ADC_CHANNEL_6, &chan_config);
    }
}

static int wait_for_level(int level, uint32_t timeout_us)
{
    int64_t start = esp_timer_get_time();
    while (gpio_get_level(PIN_DHT22) != level) {
        if ((esp_timer_get_time() - start) > timeout_us) {
            return -1;
        }
    }
    return (int)(esp_timer_get_time() - start);
}

bool dht22_read(float *temp, float *hum)
{
    uint8_t data[5] = {0, 0, 0, 0, 0};

    // Step 1: Host start signal (pull LOW for 20ms)
    gpio_set_direction(PIN_DHT22, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_DHT22, 0);
    esp_rom_delay_us(20000);

    // Pull HIGH for 30us
    gpio_set_level(PIN_DHT22, 1);
    esp_rom_delay_us(30);

    // Switch to input mode with pullup
    gpio_set_direction(PIN_DHT22, GPIO_MODE_INPUT);

    // Wait for DHT response (LOW ~80us, HIGH ~80us)
    if (wait_for_level(0, 100) < 0) return false;
    if (wait_for_level(1, 100) < 0) return false;
    if (wait_for_level(0, 100) < 0) return false;

    // Read 40 bits
    for (int i = 0; i < 40; i++) {
        // Wait for leading LOW (50us)
        if (wait_for_level(1, 80) < 0) return false;

        // Measure HIGH duration (26-28us = 0, 70us = 1)
        int64_t high_start = esp_timer_get_time();
        if (wait_for_level(0, 100) < 0) return false;
        int64_t duration = esp_timer_get_time() - high_start;

        if (duration > 45) {
            data[i / 8] |= (1 << (7 - (i % 8)));
        }
    }

    // Checksum verification
    uint8_t sum = (data[0] + data[1] + data[2] + data[3]) & 0xFF;
    if (sum != data[4]) {
        return false;
    }

    // Convert values
    float raw_hum = ((data[0] << 8) | data[1]) * 0.1f;
    float raw_temp = (((data[2] & 0x7F) << 8) | data[3]) * 0.1f;
    if (data[2] & 0x80) {
        raw_temp = -raw_temp;
    }

    *hum = raw_hum;
    *temp = raw_temp;
    last_valid_temp = raw_temp;
    last_valid_hum = raw_hum;
    return true;
}

int ldr_read_light_level(void)
{
    if (adc1_handle == nullptr) {
        return 50; // default mid-level fallback
    }

    int raw_val = 0;
    if (adc_oneshot_read(adc1_handle, ADC_CHANNEL_6, &raw_val) == ESP_OK) {
        /*
         * Wokwi Photoresistor Sensor Module (AO pin):
         * - Maximum illumination (100,000 lux): raw ADC reaches ~3900-4095 -> 100% (Bright)
         * - Minimum illumination (0.1 lux): raw ADC is ~30-200 -> 0% (Dim)
         * 
         * Direct linear calibrated mapping:
         * raw_val <= 200  -> 0% (Dim)
         * raw_val >= 3950 -> 100% (Bright)
         */
        float pct = ((float)(raw_val - 200) * 100.0f) / 3750.0f;
        int scaled = (int)(pct + 0.5f);
        if (scaled < 0) scaled = 0;
        if (scaled > 100) scaled = 100;
        return scaled;
    }

    return 50;
}

void sensor_task(void *pvParameters)
{
    TickType_t lastWakeTime = xTaskGetTickCount();
    SensorData reading;

    for (;;) {
        float t = last_valid_temp;
        float h = last_valid_hum;

        /* Try reading from DHT22 */
        if (!dht22_read(&t, &h)) {
            /* Fallback to last known good reading */
            t = last_valid_temp;
            h = last_valid_hum;
        }

        int light = ldr_read_light_level();
        bool motion = motion_read_current();

        reading.temperature = t;
        reading.humidity = h;
        reading.lightLevel = light;
        reading.motionDetected = motion;

        /* Send to Queue for consumers (AlarmTask & DisplayTask) */
        if (sensorQueue != nullptr) {
            xQueueSend(sensorQueue, &reading, 0);
        }

        /* Update display cache immediately */
        display_update_sensor_data(&reading);

        /* Log reading in thread-safe manner */
        safe_log("SENSOR", "T=%.1f C | H=%.1f %% | Light=%d %% | Motion=%s",
                 reading.temperature,
                 reading.humidity,
                 reading.lightLevel,
                 reading.motionDetected ? "YES" : "NO");

        /* Mandatory periodic execution using vTaskDelayUntil (2000 ms) */
        vTaskDelayUntil(&lastWakeTime, pdMS_TO_TICKS(2000));
    }
}
