"""Constants for the Net2Grid integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final

DOMAIN: Final = "net2grid"
LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=30)

SERVICE_DEVICE: Final = "device"
SERVICE_SMARTBRIDGE: Final = "smartbridge"

SERVICES: dict[str, str] = {
    SERVICE_SMARTBRIDGE: "SmartBridge",
}
