"""triad-audio-matrix"""

from homeassistant import core

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import CONF_OUTPUTS, CONF_SOURCES, MATRIX_OBJECT, DOMAIN
from .triad_matrix import TriadMatrixOutputChannel

import logging
# import homeassistant.helpers.config_validation as cv
# import voluptuous as vol

# from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

from homeassistant.components.media_player import (
    ENTITY_ID_FORMAT,
    MediaPlayerEntity,
    MediaPlayerEnqueue,
)
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
    MediaPlayerState,
)

from homeassistant.const import (
    # ATTR_ENTITY_ID,
    # ATTR_FRIENDLY_NAME,
    # CONF_NAME,
    STATE_ON,
    STATE_OFF,
    CONF_HOST,
    CONF_PORT
)

_LOGGER = logging.getLogger(__name__)

# This sets the name used in configuration.yaml
CONF_ON_VOLUME = "on_volume"
CONF_CHANNEL = "channel"
MATRIX_ID = "triad_matrix_id"

DEFAULT_VOLUME: int = 15

SUPPORT_TRIAD_AMS = (
    MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.PLAY_MEDIA
)

# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
#     {
#         vol.Required(CONF_NAME): cv.string,
#         vol.Optional(CONF_ON_VOLUME, default=DEFAULT_VOLUME): cv.positive_int, # type: ignore
#         vol.Required(CONF_HOST): cv.string,
#         vol.Required(CONF_CHANNEL): cv.positive_int,
#         vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port, # type: ignore
#         vol.Optional(CONF_SOURCE_LIST): cv.ensure_list,
#         vol.Optional(MATRIX_ID): cv.string,
#     }
# )

media_players = []


# async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
#     #entity_name = config.get(CONF_NAME)
#     #on_volume = config.get(CONF_ON_VOLUME)
#     host = config.get(CONF_HOST)
#     port = config.get(CONF_PORT)
#     channel = config.get(CONF_CHANNEL)
#     source_list = config.get(CONF_SOURCES)
#     zone_list = config.get(CONF_OUTPUTS)
#     #matrix_id = config.get(MATRIX_ID)

#     for idx, zone in zone_list:
#         entity = TriadAudioMatrixMediaPlayer(
#             hass, zone.name, 15, host, port, idx, source_list, MATRIX_ID
#         )
#         triad_entities.append(entity)

#     async_add_entities(
#         triad_entities
#     )
@core.callback

# def _get_sources_from_dict(data):
#     sources_config = data[CONF_SOURCES]

#     source_id_name = {int(index): name for index, name in sources_config.items()}

#     source_name_id = {v: k for k, v in source_id_name.items()}

#     source_names = sorted(source_name_id.keys(), key=lambda v: source_name_id[v])

#     return [source_id_name, source_name_id, source_names]


# @core.callback
# def _get_sources(config_entry):
#     if CONF_SOURCES in config_entry.options:
#         data = config_entry.options
#     else:
#         data = config_entry.data
#     return _get_sources_from_dict(data)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Triad Audio Matrix platform."""

    port = config_entry.data[CONF_PORT]
    host = config_entry.data[CONF_HOST]

    #matrix = hass.data[DOMAIN][config_entry.entry_id][MATRIX_OBJECT]

    #if CONF_SOURCES in config_entry.options:
        #sources = config_entry.options[CONF_SOURCES]
    #else:
    #    sources = config_entry.data[CONF_SOURCES]

    _LOGGER.info("config_entry.data:")
    _LOGGER.info(config_entry.data)
    sources = config_entry.data[CONF_SOURCES]
    zones = config_entry.data[CONF_OUTPUTS]

    for z in zones:
        channel = z['channel']
        name = z['name']
        _LOGGER.info("Adding channel %d with name %s", channel, name)
        media_players.append(
            TriadAudioMatrixMediaPlayer(hass, name, DEFAULT_VOLUME, host, port, channel, sources, "")
        )

    # only call update before add if it's the first run so we can try to detect zones
    #first_run = hass.data[DOMAIN][config_entry.entry_id][FIRST_RUN]
    #async_add_entities(entities, first_run)
    async_add_entities(media_players)

class TriadAudioMatrixMediaPlayer(MediaPlayerEntity):
    # Research at https://developers.home-assistant.io/docs/core/entity/media-player/
    # _attr_device_class =

    def __init__(
        self, hass, name, on_volume, host, port, channel, source_list, matrix_id
    ):
        self.hass = hass
        self._matrix_id = matrix_id
        self._domain = __name__.split(".")[-2]
        self._name = name
        self._source = None
        self._source_list = source_list
        self._on_volume = on_volume / 100
        self._mute_volume = 0
        self._state = STATE_OFF
        self._available = True
        self._muted = False
        self._group_members = []
        self._channel = channel

        self._ampChannel = TriadMatrixOutputChannel(host, port, channel)

    async def async_update(self):
        # Not sure if update(self) is required.
        _LOGGER.warn("update...")

    @property
    def should_poll(self):
        return False

    @property
    def icon(self) -> str | None:
        """Return the icon."""
        return "mdi:speaker"

    @property
    def is_volume_muted(self):
        return self._muted

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def media_title(self):
        """Return the current source as medial title."""
        if self._source is None:
            return None
        else:
            return self._source["name"]

    @property
    def source(self):
        if self._source is None:
            return None
        else:
            return self._source["name"]

    @property
    def source_list(self):
        sources = []
        if self._source_list is None and self._matrix_id is not None:
            _LOGGER.warn("matrix_id: %s", self._matrix_id)
            matrix_entity = self.hass.states.get(self._matrix_id)
            _LOGGER.warn("matrix_entity: %s", matrix_entity)
            self._source_list = matrix_entity.attributes["source_list"] # type: ignore
            _LOGGER.warn("source list %s", self._source_list)

        for s in self._source_list:
            sources.append(s["name"])
        return sources

    @property
    def group_members(self):
        return self._group_members

    @property
    def group(self):
        return self._group_members

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._ampChannel.volume

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_TRIAD_AMS

    async def async_pause_spotify_if_not_used(self):
        # if this is the last player with this spotify source, pause spotify
        if self._source is not None and "spotify_id" in self._source:
            pause_spotify = True

            for entity in media_players:
                if (
                    entity.source == self._source["name"]
                    and entity.entity_id != self.entity_id
                ):
                    pause_spotify = False
                    break

            if pause_spotify:
                action_data = {"entity_id": self._source["spotify_id"]}
                entity = self.hass.states.get(self._source["spotify_id"])

                if entity.state == MediaPlayerState.PLAYING: # type: ignore
                    await self.hass.services.async_call(
                        "media_player", "media_pause", action_data
                    )

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        if mute:
            self._muted = True
            self._mute_volume = self._ampChannel.volume
            self._ampChannel.volume = 0
            # _LOGGER.warn("volume set to  zero to mute")
        else:
            self._muted = False
            self._ampChannel.volume = self._mute_volume
            # _LOGGER.warn("volume set to pre-mute level")
        self.schedule_update_ha_state()

    async def async_select_source(self, source):
        for s in self._source_list:
            if s["name"] == source:
                if self._state != STATE_ON:
                    await self.async_turn_on()
                else:
                    await self.async_pause_spotify_if_not_used()

                self._source = s
                self._ampChannel.source = int(s["channel"])

                if "spotify_id" in self._source:
                    action_data = {
                        "entity_id": self._source["spotify_id"],
                        "source": self._source["name"],
                    }
                    await self.hass.services.async_call(
                        "media_player", "select_source", action_data, True
                    )
                break

        self.schedule_update_ha_state()
        # _LOGGER.warn("Source input is " + str(self._source["input"]))
        # _LOGGER.warn("Source set to " + str(self._source["name"]))

    async def async_turn_on(self):
        # _LOGGER.warn("Turning on...")
        self._ampChannel.volume = self._on_volume
        self._state = STATE_ON
        self.schedule_update_ha_state()

    async def async_turn_off(self):
        # _LOGGER.warn("Turning off...")
        self._ampChannel.volume = 0
        self._ampChannel.source = 0

        await self.async_pause_spotify_if_not_used()

        self._source = None
        # result = self._ampChannel.turn_off()
        self._state = STATE_OFF
        self.schedule_update_ha_state()

    async def async_volume_up(self):
        self._ampChannel.volume = self._ampChannel.volume + 0.02
        self.schedule_update_ha_state()
        # _LOGGER.warn("volume set to " + str(self._ampChannel.volume))

    async def async_volume_down(self):
        self._ampChannel.volume = self._ampChannel.volume - 0.02
        self.schedule_update_ha_state()
        # _LOGGER.warn("volume set to " + str(self._ampChannel.volume))

    async def async_set_volume_level(self, volume):
        self._ampChannel.volume = volume
        self.schedule_update_ha_state()
        # _LOGGER.warn("volume set to " + str(self._ampChannel.volume))

    async def async_media_play_pause(self):
        if self._state != STATE_ON:
            await self.async_turn_on()

        if self._source is None:
            if self._source_list is not None and len(self._source_list) > 0:
                await self.async_turn_on()
                s = self._source_list[0]
                await self.async_select_source(s["name"])
                # give spotify time to select the source, otherwise playing will fail below
                # time.sleep(3)

        if self._source is not None and "spotify_id" in self._source:
            action_data = {"entity_id": self._source["spotify_id"]}
            await self.hass.services.async_call(
                "media_player", "media_play_pause", action_data
            )
            self.schedule_update_ha_state()

    async def async_play_media(
        self,
        media_type: str,
        media_id: str | list[str],
        enqueue: MediaPlayerEnqueue | None = None,
        announce: bool | None = None,
        **kwargs: any # type: ignore
    ) -> None:
        _LOGGER.warn(
            "async_play_media, media_type: %s, media_id: %s", media_type, media_id
        )
        action_data = {"name": media_id, "limit": 1, "media_type": ["track"]}
        result = await self.hass.services.async_call(
            "mass", "search", action_data, True, None, None, True
        )
        _LOGGER.warn(
            "async_play_media, search result: %s, media_id: %s", result, media_id
        )

        uri = result["tracks"][0]["uri"] # type: ignore
        _LOGGER.warn("spotify URI: %s", uri)

    async def async_media_play(self):
        if self._state != STATE_ON:
            await self.async_turn_on()

        if self._source is None:
            if self._source_list is not None and len(self._source_list) > 0:
                s = self._source_list[0]
                await self.async_select_source(s["name"])
                # give spotify time to select the source, otherwise playing will fail below
                # time.sleep(3)
        if self._source is not None and "spotify_id" in self._source:
            action_data = {"entity_id": self._source["spotify_id"]}
            await self.hass.services.async_call(
                "media_player", "media_play", action_data
            )

            self.schedule_update_ha_state()

    async def async_media_next_track(self):
        if self._source is not None and "spotify_id" in self._source:
            action_data = {"entity_id": self._source["spotify_id"]}
            await self.hass.services.async_call(
                "media_player", "media_next_track", action_data
            )
            self.schedule_update_ha_state()

    async def async_join_players(self, group_members):
        """Join `group_members` as a player group with the current player."""
        # _LOGGER.warn("async join for %s with %s", self._name, group_members)

        # if self._channel == 0:
        #     for entity_id in group_members:
        #         action_data = { "entity_id" : entity_id, 'group_members': group_members }
        #         await self.hass.services.async_call('media_player', 'join', action_data)

        # self._group_members.append(group_members)

        # self.schedule_update_ha_state()

        self._group_members = list(
            set(self._group_members + [self.entity_id] + group_members)
        )

        self.async_write_ha_state()

    async def async_unjoin_player(self):
        """Remove this player from any group."""
        # _LOGGER.warn("async unjoin called on %s", self.entity_id)