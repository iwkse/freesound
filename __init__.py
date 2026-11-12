# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Support reloading the add-on (F8 / Reload Scripts), as described in
# https://developer.blender.org/docs/handbook/extensions/addon_dev_setup/#reloading-scripts
_needs_reload = "bpy" in locals()

from os.path import join

import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Scene, AddonPreferences
from bpy.props import StringProperty, BoolProperty, PointerProperty

from . import (
    freesound_api,
    freesound,
    ui,
)

if _needs_reload:
    import importlib
    # Dependencies first: freesound uses freesound_api, ui uses freesound.
    freesound_api = importlib.reload(freesound_api)
    freesound = importlib.reload(freesound)
    ui = importlib.reload(ui)

class ApiAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    """Check the check the check"""
    bl_idname = __package__

    freesound_api : StringProperty(
        subtype = "PASSWORD",
        name = "Insert your API Key",
        description = "Your freesound API Key. Get it at https://freesound.org/apiv2/apply/",
        default = ""
    )

    freesound_project_folder_pattern : StringProperty(
        name = "Folder name for download",
        description = "Folder name for download in a specific folder alongside blend file",
        default = "freesound_downloads"
    )

    freesound_download_folderpath : StringProperty(
        name = "Common folder path for download",
        description = "Common folder path where freesound downloads are stored",
        subtype = 'DIR_PATH',
        default = join(bpy.utils.user_resource('DATAFILES'), "freesound_downloads")
    )

    freesound_access : BoolProperty()

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, "freesound_api")
        if not self.freesound_api:
            box.label(text="Get your API key at https://freesound.org/apiv2/apply/", icon='INFO')
        if (self.freesound_access):
            box.operator("freesound.validate", text="Validated")
        else:
            box.operator("freesound.validate", text="Validate your API Key")

        box = layout.box()
        box.prop(self, "freesound_project_folder_pattern")
        box.prop(self, "freesound_download_folderpath")


bl_info = {
    "name": "Freesound",
    "author": "Salvatore De Paolis",
    "version": (3, 0, 2),
    "blender": (2, 80, 0),
    "category": "Sequencer",
    "location": "Sequencer",
    "description": "Connect to freesound to list sounds",
    "doc_url": "https://github.com/iwkse/freesound#readme",
    "wiki_url": "https://github.com/iwkse/freesound#readme",
    "tracker_url": "https://blenderartists.org/t/freesound-add-on/671946",
    "support": "COMMUNITY"}

classes = (
        ApiAddonPreferences,
        freesound.FREESOUND_UL_List,
        freesound.Freesound_Play,
        freesound.FreeSoundItem,
        freesound.FreeSoundData,
        freesound.Freesound_Page,
        freesound.Freesound_Validate,
        freesound.Freesound_Info,
        freesound.Freesound_Add,
        freesound.Freesound_Search,
        freesound.Freesound_Next,
        freesound.Freesound_Next10,
        freesound.Freesound_Last,
        freesound.Freesound_Prev,
        freesound.Freesound_Prev10,
        freesound.Freesound_First,
        freesound.Freesound_Pause,
        ui.FREESOUND_PT_Panel,
        ui.FREESOUND_PT_subpanel_search,
        ui.FREESOUND_PT_subpanel_settings,
)

# Registration
def register():
    for cls in classes:
        register_class(cls)
# Extend the scene class here to include the addon data
    Scene.freesound_data = PointerProperty(type=freesound.FreeSoundData)
def unregister():
    # A looping preview would keep playing with no way to stop it once the
    # add-on is disabled or reloaded
    stop_playback()
    if hasattr(Scene, "freesound_data"):
        del Scene.freesound_data
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == '__main__':
    register()
