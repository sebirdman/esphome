from esphome.components import climate, sensor, switch
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import (
    CONF_ID,
    UNIT_CELSIUS,
    UNIT_PERCENT,
    UNIT_WATT,
    ICON_THERMOMETER,
    ICON_POWER,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    ICON_WATER_PERCENT,
    DEVICE_CLASS_HUMIDITY,
    CONF_INVERTED,
    CONF_ICON,
    ICON_LIGHTBULB,
    CONF_NAME,
)
from esphome.core import coroutine

from esphome.components.midea_dongle import CONF_MIDEA_DONGLE_ID, MideaDongle

AUTO_LOAD = ["climate", "sensor", "midea_dongle"]
CODEOWNERS = ["@dudanov"]

CONF_BEEPER = "beeper"
CONF_SWING_HORIZONTAL = "swing_horizontal"
CONF_SWING_BOTH = "swing_both"
CONF_OUTDOOR_TEMPERATURE = "outdoor_temperature"
CONF_POWER_USAGE = "power_usage"
CONF_HUMIDITY_SETPOINT = "humidity_setpoint"
CONF_LIGHT_SWITCH = "light_switch"
CONF_HEAT = "heat"

midea_ac_ns = cg.esphome_ns.namespace("midea_ac")
MideaAC = midea_ac_ns.class_("MideaAC", climate.Climate, cg.Component)
MideaSwitch = midea_ac_ns.class_("MideaSwitch", switch.Switch, cg.Component)

CONFIG_SCHEMA = cv.All(
    climate.CLIMATE_SCHEMA.extend(
        {
            cv.GenerateID(): cv.declare_id(MideaAC),
            cv.GenerateID(CONF_MIDEA_DONGLE_ID): cv.use_id(MideaDongle),
            cv.Optional(CONF_BEEPER, default=False): cv.boolean,
            cv.Optional(CONF_SWING_HORIZONTAL, default=False): cv.boolean,
            cv.Optional(CONF_SWING_BOTH, default=False): cv.boolean,
            cv.Optional(CONF_HEAT, default=True): cv.boolean,
            cv.Optional(CONF_OUTDOOR_TEMPERATURE): sensor.sensor_schema(
                UNIT_CELSIUS, ICON_THERMOMETER, 0, DEVICE_CLASS_TEMPERATURE
            ),
            cv.Optional(CONF_POWER_USAGE): sensor.sensor_schema(
                UNIT_WATT, ICON_POWER, 0, DEVICE_CLASS_POWER
            ),
            cv.Optional(CONF_HUMIDITY_SETPOINT): sensor.sensor_schema(
                UNIT_PERCENT, ICON_WATER_PERCENT, 0, DEVICE_CLASS_HUMIDITY
            ),
            cv.Optional(CONF_LIGHT_SWITCH): switch.SWITCH_SCHEMA.extend(
                {
                    cv.GenerateID(): cv.declare_id(MideaSwitch),
                    cv.Required(CONF_NAME): cv.string,
                    cv.Optional(CONF_INVERTED): cv.invalid(
                        "Midea switches do not support inverted mode!"
                    ),
                    cv.Optional(CONF_ICON, default=ICON_LIGHTBULB): switch.icon,
                }
            ).extend(cv.COMPONENT_SCHEMA),
        }
    ).extend(cv.COMPONENT_SCHEMA)
)


@coroutine
def new_switch(config):
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)
    yield switch.register_switch(var, config)
    yield var


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)
    yield climate.register_climate(var, config)
    paren = yield cg.get_variable(config[CONF_MIDEA_DONGLE_ID])
    cg.add(var.set_midea_dongle_parent(paren))
    cg.add(var.set_beeper_feedback(config[CONF_BEEPER]))
    cg.add(var.set_swing_horizontal(config[CONF_SWING_HORIZONTAL]))
    cg.add(var.set_swing_both(config[CONF_SWING_BOTH]))
    cg.add(var.set_heat_supported(config[CONF_HEAT]))
    if CONF_OUTDOOR_TEMPERATURE in config:
        sens = yield sensor.new_sensor(config[CONF_OUTDOOR_TEMPERATURE])
        cg.add(var.set_outdoor_temperature_sensor(sens))
    if CONF_POWER_USAGE in config:
        sens = yield sensor.new_sensor(config[CONF_POWER_USAGE])
        cg.add(var.set_power_sensor(sens))
    if CONF_HUMIDITY_SETPOINT in config:
        sens = yield sensor.new_sensor(config[CONF_HUMIDITY_SETPOINT])
        cg.add(var.set_humidity_setpoint_sensor(sens))
        cg.add(var.set_dry_mode_supported(True))
    if CONF_LIGHT_SWITCH in config:
        sens = yield new_switch(config[CONF_LIGHT_SWITCH])
        cg.add(var.set_light_switch(sens))
