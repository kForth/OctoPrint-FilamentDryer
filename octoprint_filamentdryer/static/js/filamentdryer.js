/*
 * View model for OctoPrint-FilamentDryer
 *
 * Author: Kestin Goforth
 * License: AGPLv3
 */
$(function () {
    function FilamentDryerViewModel(parameters) {
        const PLUGIN_ID = "filamentdryer";
        const FILE_EXTENSION = PLUGIN_ID;
        var self = this;

        // assign the injected parameters, e.g.:
        self.settingsView = parameters[0];
        self.loginState = parameters[1];
        self.printerState = parameters[2];
        self.access = parameters[3];
        self.filesView = parameters[4];
        self.profilesView = parameters[5];

        self.presets = ko.observableArray([]);
        self.presetOrigin = ko.observable(undefined);
        self.presetDirectory = ko.observable(undefined);
        self.filenameTemplate = ko.observable(undefined);
        self.displayTemplate = ko.observable(undefined);
        self.useHeatedBed = ko.observable(undefined);
        self.useHeatedChamber = ko.observable(undefined);

        self.filenameTemplatePreview = ko.pureComputed(function () {
            return self.presetFilename(
                self.presets()[0] || {name: "Preset", time: 4, temp: 50}
            );
        });
        self.displayTemplatePreview = ko.pureComputed(function () {
            return self.presetDisplayName(
                self.presets()[0] || {name: "Preset", time: 4, temp: 50}
            );
        });

        self.presetLocation = ko.pureComputed(function () {
            return self.presetOrigin() + "/" + self.presetDirectory();
        });

        self.presetFilename = function (preset) {
            return (
                _.sprintf(self.filenameTemplate(), {
                    name: preset.name(),
                    time: preset.time(),
                    temp: preset.temp()
                }) +
                "." +
                FILE_EXTENSION
            );
        };

        self.presetDisplayName = function (preset) {
            return _.sprintf(self.displayTemplate(), {
                name: preset.name(),
                time: preset.time(),
                temp: preset.temp()
            });
        };

        self.presetFilepath = function (preset) {
            return [self.presetDirectory(), self.presetFilename(preset)].join("/");
        };

        self.presetsFiles = ko.observableArray([]);
        self.selectedFileId = ko.observable(undefined);

        self.onBeforeBinding = function () {
            self._settings = self.settingsView.settings.plugins.filamentdryer;

            self._writeSettings(self._settings, self);
        };

        self.onSettingsBeforeSave = function () {
            self._writeSettings(self, self._settings);
        };

        self._writeSettings = function (source, target) {
            target.presets(source.presets());
            target.presetOrigin(source.presetOrigin());
            target.presetDirectory(source.presetDirectory());
            target.filenameTemplate(source.filenameTemplate());
            target.displayTemplate(source.displayTemplate());
            target.useHeatedBed(source.useHeatedBed());
            target.useHeatedChamber(source.useHeatedChamber());
        };

        self.fromCurrentData = function (data) {
            if (data && data.job && data.job.file) {
                self.selectedFileId(self._fileId(data.job.file));
            } else {
                self.selectedFileId(undefined);
            }
        };

        self.enableSelect = function (data) {
            return (
                self.filesView.isLoadAndPrintActionPossible() &&
                self.selectedFileId() !== self._fileId(data) &&
                (self.profilesView.currentProfileData().heatedBed() ||
                    self.profilesView.currentProfileData().heatedChamber())
            );
        };

        self.enableAdd = function () {
            return self.loginState.hasPermission(self.access.permissions.FILES_UPLOAD);
        };

        self.enableRemove = function (preset) {
            var busy = _.contains(
                self.printerState.busyFiles(),
                self._presetFileId(preset)
            );
            return (
                self.loginState.hasPermission(self.access.permissions.FILES_DELETE) &&
                !busy
            );
        };

        self.addPreset = function () {
            if (!self.enableAdd()) return;
            self.presets.push(self._getNewPreset());
        };

        self.removePreset = function (preset) {
            if (!self.enableRemove(preset)) return;

            self.presets.remove(preset);
        };

        self.uniquePreset = function (preset) {
            return (
                _.filter(self.presets(), function (e) {
                    return (
                        e.name() === preset.name() //&&
                        // e.time() === preset.time() &&
                        // e.temp() === preset.temp()
                    );
                }).length === 1
            );
        };

        self.showPluginSettings = function () {
            self.settingsView.show("settings_plugin_filamentdryer");
        };

        self._getNewPreset = function () {
            return ko.mapping.fromJS({
                name: _.sprintf(gettext("Preset %(num)d"), {
                    num: _.size(self.presets()) + 1
                }),
                time: 4.0,
                temp: 50
            });
        };

        self._fileId = function (file) {
            if (file && file.origin && file.path) {
                return file.origin + ":" + file.path;
            } else {
                return undefined;
            }
        };

        self._presetFileId = function (preset) {
            return self._fileId({
                origin: self.presetOrigin(),
                path: self.presetFilepath(preset)
            });
        };

        self._otherRequestInProgress = undefined;
        self.refreshPresets = function () {
            if (!self.loginState.hasPermission(self.access.permissions.FILES_LIST)) {
                return;
            }

            if (self._otherRequestInProgress !== undefined) {
                return self._otherRequestInProgress;
            }

            return (self._otherRequestInProgress = OctoPrint.files
                .listForLocation(self.presetLocation(), true, {force: true})
                .done(function (response) {
                    var files = response.children || [];
                    var presets = self.presets();
                    _.each(files, function (file) {
                        file.preset = _.filter(presets, function (preset) {
                            return self._presetFilename(preset) == file.name;
                        })[0]; // Ignore duplicate presets since they share a file.
                    });
                    self.presetsFiles(files);
                })
                .fail(function () {
                    self.presetsFiles(undefined);
                })
                .always(function () {
                    self._otherRequestInProgress = undefined;
                    self._focus = undefined;
                    self._switchToPath = undefined;
                }));
        };

        self._presetFilename = function (preset) {
            return self._snakeCase(
                _.sprintf(self.filenameTemplate(), ko.mapping.toJS(preset))
            );
        };

        // Slightly different implementation than lodash to match function in preset.py
        self._snakeCase = function (s) {
            return [
                s
                    .replace("-", " ")
                    .replace(/([A-Z]+)/, " $1")
                    .replace(/([A-Z][a-z]+)/, " $1")
                    .split(/\s/)
            ]
                .join("_")
                .toLowerCase();
        };

        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (plugin != PLUGIN_ID) {
                return;
            }

            if (data.action == "refreshPresets") {
                self.refreshPresets();
            }
        };

        self.onUserPermissionsChanged =
            self.onUserLoggedIn =
            self.onUserLoggedOut =
                function () {
                    self.refreshPresets();
                };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: FilamentDryerViewModel,
        dependencies: [
            "settingsViewModel",
            "loginStateViewModel",
            "printerStateViewModel",
            "accessViewModel",
            "filesViewModel",
            "printerProfilesViewModel"
        ],
        elements: [
            "#sidebar_plugin_filamentdryer_wrapper",
            "#settings_plugin_filamentdryer"
        ]
    });
});
