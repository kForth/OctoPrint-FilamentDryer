import octoprint.plugin
from octoprint.filemanager.destinations import FileDestinations

from octoprint_filamentdryer.preset import DEFAULT_FILENAME_TEMPLATE
from octoprint_filamentdryer.preset_manager import sync_preset_files


class FilamentDryerPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
):
    def __init__(self):
        super().__init__()
        defaults = self.get_settings_defaults()
        self._presets = defaults["presets"]
        self._presetOrigin = defaults["presetOrigin"]
        self._presetDirectory = defaults["presetDirectory"]
        self._filenameTemplate = defaults["filenameTemplate"]
        self._useHeatedBed = defaults["useHeatedBed"]
        self._useHeatedChamber = defaults["useHeatedChamber"]

        self._presetManager = None

    def _sync_presets(self):
        sync_preset_files(self._logger, self._file_manager)

    ##~~ StartupPlugin mixin

    def on_after_startup(self):
        self.read_settings()
        self._sync_presets()

    ##~~ SimpleApiPlugin

    def get_api_commands(self):
        return dict(sync=[])

    def on_api_command(self, command, data):
        if command == "sync":
            self._sync_presets()
            return "Success", 200
        else:
            return "Unknown Command", 500

    ##~~ SettingsPlugin mixin

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.read_settings()
        self._sync_presets()

    def read_settings(self):
        self._presets = self._settings.get(["presets"])
        self._presetOrigin = self._settings.get(["presetOrigin"])
        self._presetDirectory = self._settings.get(["presetDirectory"])
        self._filenameTemplate = self._settings.get(["filenameTemplate"])
        self._useHeatedBed = self._settings.get(["useHeatedBed"])
        self._useHeatedChamber = self._settings.get(["useHeatedChamber"])

    def get_settings_defaults(self):
        return {
            "presets": [
                {"name": "PLA", "temp": 50, "time": 4},
                {"name": "ABS", "temp": 70, "time": 5},
                {"name": "TPU", "temp": 45, "time": 4},
                {"name": "NYLON", "temp": 70, "time": 6},
            ],
            "presetOrigin": FileDestinations.LOCAL,
            "presetDirectory": __plugin_name__,
            "filenameTemplate": DEFAULT_FILENAME_TEMPLATE,
            "useHeatedBed": True,
            "useHeatedChamber": True,
        }

    ##~~ AssetPlugin mixin

    def get_assets(self):
        return {
            "js": ["js/filamentdryer.js"],
            "css": ["css/filamentdryer.css"],
            "less": ["less/filamentdryer.less"],
        }

    ##~~ TemplatePlugin mixin

    def get_template_configs(self):
        return [
            {
                "type": "settings",
                "name": self._plugin_name,
                "template": "filamentdryer_settings.jinja2",
                "custom_bindings": True,
            },
            {
                "type": "sidebar",
                "name": "Filament Drying",
                "template": "filamentdryer_sidebar.jinja2",
                "template_header": "filamentdryer_sidebar_header.jinja2",
                "custom_bindings": True,
                "icon": "fas fa-fan",  # fa-dryer
            },
        ]

    def get_template_vars(self):
        dict(
            presets=self._presets,
            presetOrigin=self._presetOrigin,
            presetDirectory=self._presetDirectory,
            filenameTemplate=self._filenameTemplate,
            useHeatedBed=self._useHeatedBed,
            useHeatedChamber=self._useHeatedChamber,
        )

    ##~~ ExtenstionTree hook

    def get_extension_tree(self, *args, **kwargs):
        return dict(machinecode=dict(gcode=["filamentdryer"]))

    ##~~ Softwareupdate hook

    def get_update_information(self):
        return {
            "filamentdryer": {
                "displayName": self._plugin_name,
                "displayVersion": self._plugin_version,
                # version check: github repository
                "type": "github_release",
                "user": "kforth",
                "repo": "OctoPrint-FilamentDryer",
                "current": self._plugin_version,
                # update method: pip
                "pip": "https://github.com/kforth/OctoPrint-FilamentDryer/archive/{target_version}.zip",
            }
        }


__plugin_name__ = "FilamentDryer Plugin"
__plugin_pythoncompat__ = ">=3.6,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = FilamentDryerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.filemanager.extension_tree": __plugin_implementation__.get_extension_tree,
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
    }
