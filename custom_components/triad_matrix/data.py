"""Custom types for triad_matrix."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import TriadMatrixApiClient
    from .coordinator import BlueprintDataUpdateCoordinator


type TriadMatrixConfigEntry = ConfigEntry[TriadMatrixData]


@dataclass
class TriadMatrixData:
    """Data for the Blueprint integration."""

    client: TriadMatrixApiClient
    coordinator: BlueprintDataUpdateCoordinator
    integration: Integration
