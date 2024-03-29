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

from os.path import join
from bpy.utils import register_class, unregister_class
from bpy.types import Menu
from bpy.types import Header
from bpy.types import Scene
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, BoolProperty, PointerProperty
from .ui import *
from .freesound import *

class ApiAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    """Check the check the check"""
    bl_idname = __package__

    freesound_api : StringProperty(
        subtype = "PASSWORD",
        name = "Insert your API Key",
        description = "Your freesound API Key.",
        default = "Get it here http://www.freesound.org/apiv2/apply/"
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
    "version": (2, 1),
    "blender": (2, 80, 0),
    "category": "Sequencer",
    "location": "Sequencer",
    "description": "Connect to freesound to list sounds",
    "wiki_url": "http://freesound.org/apiv2/apply",
    "tracker_url": "https://blenderartists.org/t/freesound-add-on/671946",
    "support": "COMMUNITY"}

if "bpy" in locals():
    import imp
    from . import ui
    imp.reload(ui)
else:
    from . import ui

classes = (
        ApiAddonPreferences,
        FREESOUND_UL_List,
        Freesound_Play,
        FreeSoundItem,
        FreeSoundData,
        Freesound_Page,
        Freesound_Validate,
        Freesound_Info,
        Freesound_Add,
        Freesound_Search,
        Freesound_Next,
        Freesound_Next10,
        Freesound_Last,
        Freesound_Prev,
        Freesound_Prev10,
        Freesound_First,
        Freesound_Pause,
        FREESOUND_PT_Panel,
        FREESOUND_PT_subpanel_search,
        FREESOUND_PT_subpanel_settings,
)

# Registration
def register():
    for cls in classes:
        register_class(cls)
# Extend the scene class here to include the addon data
    Scene.freesound_data = PointerProperty(type=FreeSoundData)
def unregister():
    for cls in classes:
        unregister_class(cls)

if __name__ == '__main__':
    register()
