"""Adds config flow for Blueprint."""

from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_PORT, CONF_HOST
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, LOGGER, CONF_SOURCES, CONF_OUTPUTS, CONF_CHANNEL, CONF_NAME, CONF_SPOTIFY_ID

HOST_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST, description = CONF_HOST): str,
    vol.Required(CONF_PORT, description = CONF_PORT): int}
)

SOURCE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CHANNEL): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_SPOTIFY_ID): cv.string,
        vol.Optional("add_another"): cv.boolean
    }
)

OUTPUT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CHANNEL): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional("add_another"): cv.boolean
    }
)

@callback
def configured_instances(hass):
    return [entry.data['host'] for entry in hass.config_entries.async_entries(DOMAIN)]

class TriadMatrixConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Triad Matrix."""

    def __init__(
        self
    ):
        self.sources = []
        self.outputs = []
        self.port: int = 0
        self.host: str = ""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            if CONF_HOST in user_input:
                self.host = user_input[CONF_HOST]

            if CONF_PORT in user_input:
                self.port = user_input[CONF_PORT]

            return self.async_show_form(
                step_id="get_source", data_schema=SOURCE_SCHEMA, errors=errors
            )

        return self.async_show_form(step_id="user", data_schema=HOST_SCHEMA, errors=errors)

    async def async_step_get_source(self, user_input=None):

        LOGGER.info("async_step_get_source")
        LOGGER.info(user_input)
        if user_input is not None:
            self.sources.append({
                CONF_CHANNEL: user_input[CONF_CHANNEL],
                CONF_NAME: user_input[CONF_NAME],
                CONF_SPOTIFY_ID: user_input[CONF_SPOTIFY_ID]
                })
            if user_input.get("add_another", False):
                return await self.async_step_get_source()

        return self.async_show_form(step_id="get_output", data_schema=OUTPUT_SCHEMA)

    async def async_step_get_output(self, user_input=None):

        LOGGER.info("async_step_get_output")
        LOGGER.info(user_input)
        if user_input is not None:
            self.outputs.append({
                CONF_CHANNEL: user_input[CONF_CHANNEL],
                CONF_NAME: user_input[CONF_NAME]
                })

            if user_input.get("add_another", False):
                return await self.async_step_get_output()

        return self.async_create_entry(
                title="Triad Audio Matrix " + self.host,
                data={
                    CONF_HOST: self.host,
                    CONF_PORT: self.port,
                    CONF_SOURCES: self.sources,
                    CONF_OUTPUTS: self.outputs
                },
                description="Triad Audio Matrix " + self.host
            )
