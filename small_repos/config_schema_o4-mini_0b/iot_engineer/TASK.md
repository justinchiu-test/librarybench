# The Task

I am an IoT engineer building firmware for edge devices with very limited memory. I need to delay parsing large or infrequently used config sections, inherit common network and telemetry settings across product lines, validate differently in lab vs. field, support multiple file formats (JSON/INI), bring in local secrets from .env, expand OS variables, auto-fill defaults, compose modular sub-configs, and let colleagues drop in custom telemetry parsers as plugins. I also need an interactive debug mode to prompt for missing network credentials over a serial console.

# The Requirements

* `inherit_schema`               : Share and override base network/telemetry settings across multiple device models.  
* `lazy_load_section`            : Defer loading of large “firmware_update” or “diagnostics” blocks until invoked.  
* `set_validation_context`       : Use “lab” vs. “field” validation profiles.  
* `load_config`                  : Auto-detect JSON or INI config on the device file system.  
* `load_env_file`                : Pull in local secrets from a `.env` on the SD card.  
* `register_plugin`              : Allow adding new telemetry data parsers and post-processing hooks without core changes.  
* `apply_defaults`               : Fill in defaults for sampling intervals, timeouts, and memory limits.  
* `compose_schemas`              : Build device config from modular sub-schemas (network, sensors, OTA).  
* `expand_env_vars`              : Interpolate `$DEVICE_ID` or `${FW_VERSION}` from environment.  
* `prompt_for_missing`           : Interactive serial‐console prompts for Wi-Fi SSID/password when missing.  
