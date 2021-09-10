import traceback

from appdaemon.plugins.hass.hassapi import Hass


class BaseApp(Hass):
    def notify_exception(self) -> None:
        self.notify("Encountered the following exception: \n" + traceback.format_exc())
