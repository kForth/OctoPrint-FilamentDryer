import logging
import tempfile

from octoprint.filemanager import FileManager
from octoprint.filemanager.util import StreamWrapper
from octoprint.settings import settings

import octoprint_filamentdryer.filament_dryer_script_generator as script_generator
from octoprint_filamentdryer.preset import Preset


def sync_preset_files(logger: logging.Logger, fileManager: FileManager):
    logger.info("Syncing preset files")
    clear_preset_files(logger, fileManager)
    write_preset_files(logger, fileManager)


def clear_preset_files(logger: logging.Logger, fileManager: FileManager):
    logger.info("Clearing old preset files")
    origin = settings().get(["plugins", "filamentdryer", "presetOrigin"])
    path = settings().get(["plugins", "filamentdryer", "presetDirectory"])

    fileManager.add_folder(origin, path, ignore_existing=True)  # Make sure folder exists
    files = fileManager.list_files(origin, path, recursive=False)
    for file in files[origin].values():
        fileManager.remove_file(origin, file["path"])


def write_preset_files(logger: logging.Logger, fileManager: FileManager):
    logger.info("Writing new preset files")
    origin = settings().get(["plugins", "filamentdryer", "presetOrigin"])
    path = settings().get(["plugins", "filamentdryer", "presetDirectory"])
    template = settings().get(["plugins", "filamentdryer", "filenameTemplate"])
    presets = settings().get(["plugins", "filamentdryer", "presets"])
    use_bed = settings().get(["plugins", "filamentdryer", "useHeatedBed"])
    use_chamber = settings().get(["plugins", "filamentdryer", "useHeatedChamber"])

    for preset in presets:
        try:
            logger.info("Wiring file for preset: %s", preset)
            preset = Preset.from_dict(preset)
            with tempfile.SpooledTemporaryFile() as handle:
                script_generator.create_script(
                    handle,
                    int(preset.time * 60),  # Convert hours to minutes
                    preset.temp,
                    use_bed,
                    use_chamber,
                )
                handle._file.seek(0)
                fileManager._storage(origin).add_file(
                    preset.get_filepath(path, template),
                    StreamWrapper(preset.get_filename(template), handle._file),
                    allow_overwrite=True,
                    display=preset.display,
                )
        except Exception as ex:
            logger.exception("Failed to write file for preset: %s", preset, exc_info=ex)
