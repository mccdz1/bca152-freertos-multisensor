#include <unity.h>
#include "alarm.h"
#include "input.h"
#include "sensors.h"
#include "system_state.h"

/* ========================================================================= */
/* Category 1: Temperature Alarm Decision Logic Unit Tests (5 tests)         */
/* ========================================================================= */

void test_temperature_below_low_limit(void)
{
    /* Input: 17.9 °C -> Expected: LOW_TEMPERATURE */
    TEST_ASSERT_EQUAL(AlarmState::LOW_TEMPERATURE, evaluateTemperature(17.9f));
}

void test_temperature_at_low_limit(void)
{
    /* Input: 18.0 °C -> Boundary condition: NORMAL */
    TEST_ASSERT_EQUAL(AlarmState::NORMAL, evaluateTemperature(18.0f));
}

void test_temperature_normal_mid(void)
{
    /* Input: 24.5 °C -> Normal room temperature: NORMAL */
    TEST_ASSERT_EQUAL(AlarmState::NORMAL, evaluateTemperature(24.5f));
}

void test_temperature_at_high_limit(void)
{
    /* Input: 30.0 °C -> Boundary condition: NORMAL */
    TEST_ASSERT_EQUAL(AlarmState::NORMAL, evaluateTemperature(30.0f));
}

void test_temperature_above_high_limit(void)
{
    /* Input: 30.1 °C -> Expected: HIGH_TEMPERATURE */
    TEST_ASSERT_EQUAL(AlarmState::HIGH_TEMPERATURE, evaluateTemperature(30.1f));
}

/* ========================================================================= */
/* Category 2: Display Navigation & Wraparound Unit Tests (4 tests)          */
/* ========================================================================= */

void test_navigation_forward_step(void)
{
    /* Step: TEMPERATURE -> HUMIDITY */
    TEST_ASSERT_EQUAL(DisplayMode::HUMIDITY, nextDisplayMode(DisplayMode::TEMPERATURE));
}

void test_navigation_reverse_step(void)
{
    /* Reverse Step: HUMIDITY -> TEMPERATURE */
    TEST_ASSERT_EQUAL(DisplayMode::TEMPERATURE, previousDisplayMode(DisplayMode::HUMIDITY));
}

void test_navigation_forward_wraparound(void)
{
    /* Forward Wraparound: MOTION -> TEMPERATURE */
    TEST_ASSERT_EQUAL(DisplayMode::TEMPERATURE, nextDisplayMode(DisplayMode::MOTION));
}

void test_navigation_reverse_wraparound(void)
{
    /* Reverse Wraparound: TEMPERATURE -> MOTION */
    TEST_ASSERT_EQUAL(DisplayMode::MOTION, previousDisplayMode(DisplayMode::TEMPERATURE));
}

/* ========================================================================= */
/* Category 3: System State Machine Unit Tests (4 tests)                     */
/* ========================================================================= */

void test_system_state_active_no_timeout(void)
{
    /* ACTIVE state, no motion, elapsed (5000ms) < timeout (15000ms) -> Remains ACTIVE */
    TEST_ASSERT_EQUAL(SystemState::ACTIVE,
                      evaluateSystemState(SystemState::ACTIVE, false, 5000, 15000));
}

void test_system_state_active_timeout_reached(void)
{
    /* ACTIVE state, no motion, elapsed (15000ms) >= timeout -> Transitions to INACTIVE */
    TEST_ASSERT_EQUAL(SystemState::INACTIVE,
                      evaluateSystemState(SystemState::ACTIVE, false, 15000, 15000));
}

void test_system_state_inactive_no_motion(void)
{
    /* INACTIVE state, no motion, elapsed (25000ms) -> Remains INACTIVE */
    TEST_ASSERT_EQUAL(SystemState::INACTIVE,
                      evaluateSystemState(SystemState::INACTIVE, false, 25000, 15000));
}

void test_system_state_inactive_motion_detected(void)
{
    /* INACTIVE state, motion detected -> Restores ACTIVE state immediately */
    TEST_ASSERT_EQUAL(SystemState::ACTIVE,
                      evaluateSystemState(SystemState::INACTIVE, true, 25000, 15000));
}

/* ========================================================================= */
/* Category 4: Ambient Light Calibration Unit Tests (3 tests)                */
/* ========================================================================= */

void test_light_level_at_lowest_illumination(void)
{
    /* Lowest illumination / darkness (raw ADC near 0) -> 0% */
    TEST_ASSERT_EQUAL(0, scale_light_level(0));
}

void test_light_level_at_highest_illumination(void)
{
    /* Highest illumination / direct sunlight (raw ADC 4095) -> 100% */
    TEST_ASSERT_EQUAL(100, scale_light_level(4095));
}

void test_light_level_scales_intermediate_illumination(void)
{
    /* Midpoint illumination -> 50% */
    TEST_ASSERT_EQUAL(50, scale_light_level(2048));
}

/* Runner function executing all test cases */
extern "C" int run_all_unit_tests(void)
{
    UNITY_BEGIN();

    /* Alarm tests */
    RUN_TEST(test_temperature_below_low_limit);
    RUN_TEST(test_temperature_at_low_limit);
    RUN_TEST(test_temperature_normal_mid);
    RUN_TEST(test_temperature_at_high_limit);
    RUN_TEST(test_temperature_above_high_limit);

    /* Navigation tests */
    RUN_TEST(test_navigation_forward_step);
    RUN_TEST(test_navigation_reverse_step);
    RUN_TEST(test_navigation_forward_wraparound);
    RUN_TEST(test_navigation_reverse_wraparound);

    /* State machine tests */
    RUN_TEST(test_system_state_active_no_timeout);
    RUN_TEST(test_system_state_active_timeout_reached);
    RUN_TEST(test_system_state_inactive_no_motion);
    RUN_TEST(test_system_state_inactive_motion_detected);

    /* Light level tests */
    RUN_TEST(test_light_level_at_lowest_illumination);
    RUN_TEST(test_light_level_at_highest_illumination);
    RUN_TEST(test_light_level_scales_intermediate_illumination);

    return UNITY_END();
}

#if defined(UNIT_TEST)
extern "C" void app_main(void)
{
    run_all_unit_tests();
}
#endif
