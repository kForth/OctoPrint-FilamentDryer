# OctoPrint-FilamentDryer

## Description

Most 3d printing filaments will absorb water from the surrounding area, by heating the filament for a prolonged period, most (or all) of that water can be removed.

This plugin uses your 3d printer's heated bed and/or chamber to heat the build volume for as long as needed.

**Note:** Your 3d printer *must* have a heated bed or chamber and *should* have a full enclosure.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/kforth/OctoPrint-FilamentDryer/archive/master.zip

## Configuration

After installation, restart OctoPrint and navigate to the Settings tab to configure the plugin.

### Default Presets

| Material | Time | Temp |
| :------- | ---: | ---: |
| ABS      |   5h | 70 C |
| NYLON    |   6h | 75 C |
| PLA      |   4h | 50 C |
| TPU      |   4h | 45 C |

## Warnings

- This plugin modifies files in your `uploads` folder - take care not to store anything important in the `FilamentDryer Plugin/` folder.

- Leaving your printer unattended while heated can be dangerous. Please ensure your printer's thermal runaway features are fully functional.

## License

Copyright © 2022 [Kestin Goforth](https://github.com/kforth/).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html) for more details.
