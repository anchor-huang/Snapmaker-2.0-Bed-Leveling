# -*- coding: utf-8 -*-
from __future__ import absolute_import

import octoprint.plugin
import logging
from flask import Flask, jsonify
from .DialReader import Dial

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.


class Dial_mesh_levelingPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.BlueprintPlugin
):

    def __init__(self):
        self.prcess_m420_mesh=False
        self.mesh_data=None

    ##~~ BlueprintPlugin mixin
    @octoprint.plugin.BlueprintPlugin.route("/get_dail_value", methods=["GET"])
    def get_dial_value(self):
        return jsonify({'value': Dial.read()/100})
    
    @octoprint.plugin.BlueprintPlugin.route("/get_mesh_data", methods=["GET"])
    def get_mesh_data(self):
        return jsonify({'value': self.mesh_data})

    ##~~ StartupPlugin mixin
    def on_after_startup(self):
        self._logger.info("Hello World!")

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            # put your plugin's default settings here
        )

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/dial_mesh_leveling.js"],
            css=["css/dial_mesh_leveling.css"],
            less=["less/dial_mesh_leveling.less"],
        )

    ##~~ Softwareupdate hook
    def m420_hook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        if gcode and gcode == "M420" and 'V' in cmd:
            self.m420_start=True
            self.m420_output=list()
            self._logger.info(f'cdm:{cmd}')
            self._logger.info(f'cmd_type:{cmd_type}')
            self._logger.info(f'args:{args}')
            self._logger.info(f'kwargs:{kwargs}')
        else:
            self.m420_start=False


    def parse_mesh_output(self, comm, line, *args, **kwargs):
        if self.m420_start:
            new_line=line.strip('\r\n')
            if len(new_line)==0:
                self.m420_start=False
                self.mesh_data=list()
                for line in self.m420_output[2:]:
                    self.mesh_data.append([float(item) for item in line.split()[1:]])                
                self._logger.info("Parsed Mesh Data: ")
                self._logger.info(self.mesh_data)

            else:
                self.m420_output.append(new_line)
                self._logger.info(f'Received[{new_line}]')

        return line
    
    def end_parse_mesh_output(self,comm, parsed_temps ):
        self.m420_start=False
        return parsed_temps

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            dial_mesh_leveling=dict(
                displayName="Dial_mesh_leveling Plugin",
                displayVersion=self._plugin_version,
                # version check: github repository
                type="github_release",
                user="anchor-huang",
                repo="OctoPrint-DialMeshLeveling",
                current=self._plugin_version,
                # update method: pip
                pip="https://github.com/anchor-huang/OctoPrint-DialMeshLeveling/archive/{target_version}.zip",
            )
        )





# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Dial_mesh_leveling Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
# __plugin_pythoncompat__ = ">=2.7,<3" # only python 2
__plugin_pythoncompat__ = ">=3,<4"  # only python 3
# __plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Dial_mesh_levelingPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information, 
        "octoprint.comm.protocol.gcode.received": __plugin_implementation__.parse_mesh_output, 
        "octoprint.comm.protocol.gcode.sending": __plugin_implementation__.m420_hook, 
        "octoprint.comm.protocol.temperatures.received": __plugin_implementation__.end_parse_mesh_output
    }
