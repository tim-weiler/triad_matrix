"""
Custom integration to integrate triad_matrix with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/triad_matrix

should start with what works, get that working in test environment

Then add the config flow
Add one device per zone, and one for the matrix itself.

Config flow:
- name each input
- name each output
- can these be two different forms?
- use these names to create entities with same name?  or should entities be numbered, with something that gives it a description that changes?
- the media players should be named, e.g. media_player.kitchen, but zones and inputs should be switch.output1_loudness, number.input1_gain

Each output zone device has:
- a media player
- number entity for various frequencies
- select entity for different crossover modes

entities on the matrix device:
- input gain
- input delay
- mac address (read only)


Zone device entities
- output delay (old, don't use)
- output mode (select option)
- output mono (old, don't use)
- output test tone volume
- crossover frequency
- crossover type (select option)
- subvolume offset
- input source
- output volume
- output max volume
- output start volume
- output mute
- lowshelf frequency
- lowshelf gain
- lowshelf Q
- highshelf frequency
- highshelf gain
- highshelf Q
- balance
- loudness (boolean)
"""

# """The Monoprice 6-Zone Amplifier integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from.triad_matrix import TriadMatrixOutputChannel, TriadMatrix

from .const import (
    DOMAIN,
    LOGGER,
    MATRIX_OBJECT
)

PLATFORMS = [Platform.MEDIA_PLAYER]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Triad Audio Matrix from a config entry."""
    port = entry.data[CONF_PORT]
    host = entry.data[CONF_HOST]

    matrix = TriadMatrix(port, host)

    # try:
    #     #monoprice = await hass.async_add_executor_job(get_monoprice, port)
    #     triad_matrix =
    # except SerialException as err:
    #     _LOGGER.error("Error connecting to Monoprice controller at %s", port)
    #     raise ConfigEntryNotReady from err



    # double negative to handle absence of value
    # first_run = not bool(entry.data.get(CONF_NOT_FIRST_RUN))

    # if first_run:
    #     hass.config_entries.async_update_entry(
    #         entry, data={**entry.data, CONF_NOT_FIRST_RUN: True}
    #     )

    undo_listener = entry.add_update_listener(_update_listener)

    LOGGER.info("entry.entry_id = " + entry.entry_id)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        MATRIX_OBJECT: matrix
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    #hass.data[DOMAIN][entry.entry_id][UNDO_UPDATE_LISTENER]()

    def _cleanup(monoprice) -> None:
        """Destroy the Monoprice object.

        Destroying the Monoprice closes the serial connection, do it in an executor so the garbage
        collection does not block.
        """
        del monoprice

    matrix = hass.data[DOMAIN][entry.entry_id][MATRIX_OBJECT]
    hass.data[DOMAIN].pop(entry.entry_id)

    del matrix
    return True


async def _update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)