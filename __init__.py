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

import bpy
import os.path
from bpy.types import Menu
from bpy.types import Header
from .freesound import *
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty

class ApiAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    freesound_api = bpy.props.StringProperty(
        subtype='PASSWORD',
        name="Insert your API Key",
        description="Your freesound API Key.",
        default="Get it here http://www.freesound.org/apiv2/apply/"
    )

    freesound_access = bpy.props.BoolProperty()

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "freesound_api")
        if (self.freesound_access):
            layout.operator("freesound.validate", text="Validated")
        else:
            layout.operator("freesound.validate", text="Validate your API Key")
    

bl_info = {
    "name": "Freesound",
    "author": "Salvatore De Paolis",
    "version": (2, 0),
    "blender": (2, 80, 0),
    "category": "Sequencer",
    "location": "Sequencer",
    "description": "Connect to freesound to list sounds",
    "wiki_url": "http://freesound.org/apiv2/apply",
    "support": "COMMUNITY"}

if "bpy" in locals():
    import imp
    from . import ui
    imp.reload(ui)
else:
    from . import ui

classes = (
        ApiAddonPreferences,
        FREESOUNDList,
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
)

# Registration
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
# Extend the scene class here to include the addon data
    bpy.types.Scene.freesound_data = bpy.props.PointerProperty(type=FreeSoundData)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()
