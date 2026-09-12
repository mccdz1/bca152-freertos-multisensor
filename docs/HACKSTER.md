# Real-Time FreeRTOS Multisensor Room Monitoring System on ESP32

**Author**: Michael Cadiz  
**Course**: BCA152 Microcontrollers  
**Institution**: Mindanao State University - Iligan Institute of Technology (MSU-IIT), College of Computer Studies, Department of Computer Applications  
**Instructor / Collaborator**: Paul Rodolf P. Castor ([paulrodolf.castor@g.msuiit.edu.ph](mailto:paulrodolf.castor@g.msuiit.edu.ph))  
**GitHub Repository**: [https://github.com/mccdz1/bca152-freertos-multisensor](https://github.com/mccdz1/bca152-freertos-multisensor)

---

## 1. Project Overview
The **BCA152 Real-Time Multisensor Room Monitoring System** is a concurrent, multi-threaded embedded edge device built from scratch on the **ESP32** microcontroller. Developed using the native **Espressif IoT Development Framework (ESP-IDF)** and **FreeRTOS** APIs (strictly avoiding Arduino abstraction layers), the system provides deterministic environmental tracking, responsive user interaction, acoustic anomaly alarming, and automatic power management.

Simulated on **Wokwi**, the firmware interfaces six peripherals: a **DHT22** temperature/humidity sensor, an **LDR photoresistor**, a **PIR motion sensor**, a **KY-040 rotary encoder**, an **SSD1306 128x64 OLED display**, and an **active piezo buzzer**.

---

## 2. Motivation
Traditional hobbyist embedded projects frequently rely on monolithic `loop()` structures with blocking delays (`delay()`). When multiple asynchronous events occur simultaneously—such as human rotary dial inputs while a 2-second sensor reading is underway—monolithic firmware stutters, drops user inputs, and introduces cumulative timing drift.

This project was built to address these concurrency challenges by implementing a true real-time operating system (RTOS) architecture on the ESP32. By decomposing system requirements into distinct preemptive FreeRTOS tasks with explicit priorities and synchronized communication primitives (queues, mutexes, event groups, and tick-relative delays), the device guarantees sub-millisecond input responsiveness while sustaining non-drifting 2.0-second telemetry cycles.

---

## 3. Features
- **Deterministic Periodic Telemetry**: Implements `vTaskDelayUntil()` to eliminate periodic timing jitter and drift.
- **Inter-Task Communication (IPC)**: A dedicated 5-element `SensorData` FreeRTOS queue safely transports structured telemetry across producer and consumer tasks without race conditions.
- **Thread-Safe Serial Logging**: Shared UART console access is synchronized using a binary FreeRTOS `serialMutex`, ensuring logs are never garbled or interleaved.
- **Event-Driven Signal Dispatch**: A centralized `systemEventGroup` coordinates `EVENT_ACTIVE`, `EVENT_MOTION`, and `EVENT_ALARM` flags.
- **Autonomous Anomaly Detection**: Temperature thresholds are continuously monitored; readings outside 18.0 °C to 30.0 °C trigger immediate buzzer alarms.
- **Quadrature Rotary Navigation**: KY-040 encoder provides continuous page navigation with circular wraparound across 4 telemetry pages:
  $$\text{Temperature} \longleftrightarrow \text{Humidity} \longleftrightarrow \text{Light Level} \longleftrightarrow \text{Motion Status}$$
- **Automated Power-Saving State Machine**: The system monitors physical occupancy via PIR motion. If no activity is detected for 15 seconds, it automatically transitions from `ACTIVE` to `INACTIVE`, turning off the OLED display to conserve energy while maintaining background surveillance.
- **100% Automated Unit Test Verification**: Incorporates 13 deterministic, hardware-independent unit tests using Unity with 100% pass rate.

---

## 4. Components & Hardware Bill of Materials
| Component | Type / Model | Interface | Purpose |
|---|---|---|---|
| **Microcontroller** | ESP32-DevKitC-V4 (Xtensa Dual-Core) | System Master | Core execution and FreeRTOS scheduling |
| **Environmental Sensor** | DHT22 (AM2302) | 1-Wire Digital (GPIO 4) | Temperature (-40 to 80 °C) & Relative Humidity |
| **Ambient Light Sensor** | Photoresistor (LDR) Sensor | Analog ADC1_CH6 (GPIO 34) | Relative room illumination (0 to 100%) |
| **Presence Detector** | PIR Motion Sensor (HC-SR501) | Digital In (GPIO 13) | Human presence and activity tracking |
| **User Input Dial** | KY-040 Rotary Encoder | Digital In (GPIO 18, 19, 5) | Quadrature UI page switching & wake trigger |
| **Information Display** | SSD1306 OLED (128x64) | I2C Master @ 400kHz (GPIO 21, 22) | Real-time graphical dashboard |
| **Alarm Actuator** | Active Piezo Buzzer | Digital Out (GPIO 15) | Audible acoustic alarm on out-of-bounds metrics |

---

## 5. Circuit Schematic & Wiring
The Wokwi simulation circuit connects all peripherals to dedicated ESP32 GPIOs:

![Wokwi Circuit Schematic](docs/wokwi_circuit.png)

### Pinout Mapping:
- **SSD1306 OLED**: SDA $\rightarrow$ GPIO 21, SCL $\rightarrow$ GPIO 22, VCC $\rightarrow$ 3.3V, GND $\rightarrow$ GND
- **DHT22**: SDA $\rightarrow$ GPIO 4 (Open-Drain with internal pull-up), VCC $\rightarrow$ 3.3V, GND $\rightarrow$ GND
- **LDR Sensor**: AO $\rightarrow$ GPIO 34 (ADC1 Channel 6, 12-bit attenuation 12dB), VCC $\rightarrow$ 3.3V, GND $\rightarrow$ GND
- **PIR Sensor**: OUT $\rightarrow$ GPIO 13, VCC $\rightarrow$ 3.3V, GND $\rightarrow$ GND
- **KY-040 Encoder**: CLK $\rightarrow$ GPIO 18, DT $\rightarrow$ GPIO 19, SW $\rightarrow$ GPIO 5, VCC $\rightarrow$ 3.3V, GND $\rightarrow$ GND
- **Buzzer**: Positive $\rightarrow$ GPIO 15, Negative $\rightarrow$ GND

---

## 6. System Architecture
The application is structured into a 5-layer modular embedded hierarchy:

![System Architecture](docs/system_architecture.png)

1. **Hardware Layer**: Simulated physical transducers in Wokwi.
2. **ESP-IDF Driver Layer**: Hardware Abstraction Layer (HAL) interfacing I2C, ADC Oneshot, and GPIO peripherals.
3. **RTOS Subsystem**: FreeRTOS preemption scheduler, queues, mutexes, and event flags.
4. **Application Tasks**: Decoupled, single-responsibility concurrent tasks.
5. **Presentation Layer**: Visual OLED screens and acoustic signaling.

---

## 7. FreeRTOS Architecture & Task Design
The system runs six concurrent tasks, each assigned an explicit priority based on scheduling urgency:

![FreeRTOS Architecture](docs/freertos_architecture.png)

### FreeRTOS Task Schedule:
| Task Name | Priority | Period / Trigger | IPC Mechanism | Typical Blocked Condition | Responsibility |
|---|---|---|---|---|---|
| **MotionTask** | 3 | 100 ms periodic | Event Group (`EVENT_MOTION`) | `vTaskDelay(100ms)` | Detects PIR edge events, updates motion state |
| **InputTask** | 3 | 10 ms periodic | Direct / Shared Mode | `vTaskDelay(10ms)` | Samples encoder quadrature signals, triggers navigation |
| **SensorTask** | 2 | 2000 ms periodic | Queue (`sensorQueue`) | `vTaskDelayUntil(&wake, 2000ms)` | Acquires DHT22 and LDR data, broadcasts packet |
| **AlarmTask** | 2 | Event-driven (Queue) | Queue (`sensorQueue`) | `xQueueReceive(sensorQueue)` | Evaluates temperature bounds, activates buzzer |
| **StateTask** | 2 | 500 ms periodic | Event Group (`EVENT_ACTIVE`) | `vTaskDelay(500ms)` | Inactivity tracking and power mode transitions |
| **DisplayTask** | 1 | 150 ms periodic | Queue / Shared Cache | `xQueueReceive() / Delay` | Single owner of OLED, renders dashboard |

### Scheduling Justifications:
- **Priority 3 (`MotionTask`, `InputTask`)**: These tasks service interactive physical events (human rotation and motion pulses). They require high urgency to prevent missed quadrature transitions and provide immediate user feedback.
- **Priority 2 (`SensorTask`, `AlarmTask`, `StateTask`)**: Core supervisory processing. Sensor sampling runs periodically every 2 seconds. The alarm task reacts immediately upon receiving a packet.
- **Priority 1 (`DisplayTask`)**: Visual rendering over I2C requires transmission time. Rendering can tolerate milliseconds of latency without human perception, so it runs at the lowest priority to prevent starving mission-critical tasks.

---

## 8. How It Works

### Drift-Free Periodic Sampling (`vTaskDelayUntil`)
While `vTaskDelay(period)` delays relative to the moment it is invoked, the execution time of sensor readout ($\Delta t_{\text{exec}}$) causes the actual period to expand to $\text{period} + \Delta t_{\text{exec}}$, resulting in severe cumulative timing drift over hours of operation.

`SensorTask` uses `vTaskDelayUntil(&lastWakeTime, pdMS_TO_TICKS(2000))`:
$$\text{Next Wake Time} = \text{Last Wake Time} + 2000\text{ ms}$$
This guarantees a rigid, exact 2000 ms sampling period regardless of I/O latency.

### Power Management State Machine
The device implements an energy-conscious state machine:

![State Machine](docs/state_machine.png)

- **ACTIVE State**: Full display brightness, real-time UI refresh, audio alarms enabled.
- **INACTIVE State**: Inactivity timer triggers after 15 seconds without motion. The display is blanked (`display_set_power(false)`), reducing I2C bus traffic and simulated screen power, while low-power background PIR monitoring remains vigilant.
- **Reactivation**: Any human presence detected by the PIR sensor or rotary dial instantly restores the `ACTIVE` state.

---

## 9. Testing and Verification

### 1. Automated Unit Tests (Unity)
Thirteen automated unit tests verify all pure, hardware-independent decision algorithms:
```
test_main.cpp:32:test_temperature_below_low_limit:PASS
test_main.cpp:38:test_temperature_at_low_limit:PASS
test_main.cpp:44:test_temperature_normal_mid:PASS
test_main.cpp:50:test_temperature_at_high_limit:PASS
test_main.cpp:56:test_temperature_above_high_limit:PASS
test_main.cpp:64:test_navigation_forward_step:PASS
test_main.cpp:70:test_navigation_reverse_step:PASS
test_main.cpp:76:test_navigation_forward_wraparound:PASS
test_main.cpp:82:test_navigation_reverse_wraparound:PASS
test_main.cpp:90:test_system_state_active_no_timeout:PASS
test_main.cpp:97:test_system_state_active_timeout_reached:PASS
test_main.cpp:104:test_system_state_inactive_no_motion:PASS
test_main.cpp:111:test_system_state_inactive_motion_detected:PASS
-----------------------
13 Tests 0 Failures 0 Ignored -> ALL PASSED
```

### 2. Static Code Analysis (`pio check`)
Static analysis executed via `cppcheck` with `--skip-packages`:
- **Defects Found**: 0
- **High Severity**: 0
- **Medium Severity**: 0
- **Low Severity**: 0
- **Result**: PASSED in 1.33 seconds.

### 3. Functional Verification Matrix
| Test ID | Description | Stimulus | Expected Output | Observed Result | Status |
|---|---|---|---|---|---|
| **FT-01** | Temperature update | Slide DHT22 temp slider | OLED temperature reflects change | Display updated to new temp | **PASS** |
| **FT-02** | Humidity update | Slide DHT22 humidity slider | OLED humidity reflects change | Display updated to new humidity | **PASS** |
| **FT-03** | Ambient light reading | Adjust LDR slider | Light level scales from 0 to 100% | Linear percentage displayed | **PASS** |
| **FT-04** | Encoder CW navigation | Rotate encoder clockwise | Switches page to next parameter | Temp $\rightarrow$ Hum $\rightarrow$ Light $\rightarrow$ Motion | **PASS** |
| **FT-05** | Encoder CCW navigation | Rotate encoder counter-clockwise | Switches page to previous parameter | Motion $\rightarrow$ Light $\rightarrow$ Hum $\rightarrow$ Temp | **PASS** |
| **FT-06** | High temperature alarm | Set temperature to 32.0 °C | Buzzer activates, OLED displays ALARM | Buzzer sounded, OLED showed ALARM | **PASS** |
| **FT-07** | Temperature normalization | Return temperature to 24.5 °C | Buzzer deactivates, status NORMAL | Buzzer silenced, state cleared | **PASS** |
| **FT-08** | Motion detection | Trigger PIR sensor | EVENT_MOTION set, state confirmed ACTIVE | System asserted ACTIVE | **PASS** |
| **FT-09** | Inactivity timeout | Wait 15 seconds without motion | System enters INACTIVE, OLED blanks | OLED turned off at 15s mark | **PASS** |
| **FT-10** | Wake on motion | Trigger PIR sensor during INACTIVE | System restores ACTIVE, OLED turns ON | OLED lit up instantly | **PASS** |

---

## 10. Demonstration
The system in action showing OLED screens and serial logging stream:

![System Running](docs/system_running.png)

---

## 11. Challenges Encountered & Solutions
1. **CMake Git-Data Hook in Home Directory**:
   - *Problem*: CMake repeatedly failed during the bootloader build because an untracked `.git` repository existed in the user home directory with an uncommitted `refs/heads/master` pointer.
   - *Solution*: Implemented `pre_build_git_fix.py` in PlatformIO's `extra_scripts` pipeline to synthesize mock commit references in all `.pio/build` subdirectories prior to CMake evaluation.
2. **Display Contention & I2C Bus Collisions**:
   - *Problem*: Allowing both `SensorTask` and `InputTask` to render to the OLED caused I2C bus lockups.
   - *Solution*: Strictly enforced the **single-owner design pattern**, making `DisplayTask` the sole entity permitted to interact with the I2C peripheral, fed via asynchronous queue packets and thread-safe caches.
3. **Serial Terminal Interleaving**:
   - *Problem*: When multiple tasks logged status simultaneously, ASCII characters overlapped and produced unreadable logs.
   - *Solution*: Engineered `safe_log()` wrapped in `serialMutex`, ensuring complete lines are written atomically.

---

## 12. Lessons Learned
- Decoupling deterministic business logic from hardware drivers allows high-speed unit testing on development machines without needing hardware in the loop.
- Task priorities must represent **scheduling urgency** rather than perceived "importance".
- `vTaskDelayUntil()` is essential for any real-world sensor node requiring precise interval math (such as numerical integration or Kalman filtering).

---

## 13. Limitations & Future Work
- **Simulation Constraints**: Wokwi simulates ideal digital signals without contact bouncing or analog electrical noise.
- **Future Improvements**:
  - Implement Non-Volatile Storage (NVS) to save user-configured alarm thresholds across reboots.
  - Implement ESP32 Deep Sleep mode using the ULP co-processor for ultra-low battery operation.
  - Connect to MQTT/AWS IoT Core over Wi-Fi for cloud dashboard visualization.

---

## 14. References & Acknowledgments
- [FreeRTOS Official Kernel Documentation & API Reference](https://www.freertos.org/)
- [Espressif ESP-IDF Programming Guide (v5.x/v6.x)](https://docs.espressif.com/projects/esp-idf/)
- [Wokwi Embedded Systems Simulator](https://wokwi.com/)
- Course Syllabus & Instruction: **Paul Rodolf P. Castor** (`paulrodolf.castor@g.msuiit.edu.ph`), Department of Computer Applications, MSU-IIT.
