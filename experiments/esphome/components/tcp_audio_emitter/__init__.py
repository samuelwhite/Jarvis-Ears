import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import microphone
from esphome.const import CONF_ID, CONF_MICROPHONE, CONF_PORT


CONF_HOST = "host"
CONF_AUTO_START = "auto_start"

DEPENDENCIES = ["wifi"]

tcp_audio_emitter_ns = cg.esphome_ns.namespace("tcp_audio_emitter")
TCPAudioEmitter = tcp_audio_emitter_ns.class_("TCPAudioEmitter", cg.Component)


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(TCPAudioEmitter),
        cv.Required(CONF_MICROPHONE): cv.use_id(microphone.Microphone),
        cv.Required(CONF_HOST): cv.string_strict,
        cv.Optional(CONF_PORT, default=8765): cv.port,
        cv.Optional(CONF_AUTO_START, default=True): cv.boolean,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    mic = await cg.get_variable(config[CONF_MICROPHONE])
    cg.add(var.set_microphone(mic))
    cg.add(var.set_host(config[CONF_HOST]))
    cg.add(var.set_port(config[CONF_PORT]))
    cg.add(var.set_auto_start(config[CONF_AUTO_START]))
