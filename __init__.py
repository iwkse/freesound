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

bl_info = {
    "name": "Freesound",
    "author": "Salvatore De Paolis",
    "version": (0, 1),
    "blender": (2, 77, 1),
    "category": "Sequencer",
    "location": "Sequencer",
    "description": "Connect to freesound to list sounds",
    "support": "COMMUNITY"}


if "bpy" in locals():
    import imp
    imp.reload(ui)
else:
    from . import ui

import bpy
import os.path
from bpy.types import Menu
from bpy.types import Header
from . import freesound

class FreeSoundItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
        name="Sound name",
        description="The name of this sound",
        default="Name"
    )
    id = bpy.props.StringProperty(
        name="ID",
        description="The ID of this sound",
        default="ID"
    )

# Defines one instance of the addon data (one per scene)
class FreeSoundData(bpy.types.PropertyGroup):
    freesound_api = bpy.props.StringProperty(
        name="Api key",
        description="Your freesound API Key.",
        default="Get it here http://www.freesound.org/apiv2/apply/"
    )
    freesound_access = bpy.props.BoolProperty(
        description=(
            'Access to Freesound API'
        )
    )
    search_item = bpy.props.StringProperty(
        description=(
            'Sound to search'
        )
    )
    active_list_item = bpy.props.IntProperty()
    freesound_list = bpy.props.CollectionProperty(type=FreeSoundItem)

class FREESOUNDList(bpy.types.UIList):

    def draw_item(self,
                  context,
                  layout,
                  data,
                  item,
                  icon,
                  active_data,
                  active_propname
                  ):
        addon_data = bpy.context.scene.freesound_data
        sounds = addon_data.freesound_list

        # Check which type of primitive, separate draw code for each
        if item.kind == 'POINT':
            layout.label(item.name, icon="LAYER_ACTIVE")
        elif item.kind == 'LINE':
            layout.label(item.name, icon="MAN_TRANS")
        elif item.kind == 'PLANE':
            layout.label(item.name, icon="OUTLINER_OB_MESH")
        elif item.kind == 'CALCULATION':
            layout.label(item.name, icon="NODETREE")
        elif item.kind == 'TRANSFORMATION':
            layout.label(item.name, icon="MANIPUL")

    
# Freesound Connect
class Freesound_Connect(bpy.types.Operator):
    bl_label = 'Connect'
    bl_idname = 'freesound.connect'
    bl_description = 'Connect to Freesound'
    bl_options = {'REGISTER', 'UNDO'}
    client = freesound.FreesoundClient()
    def execute(self, context):
        addon_data = context.scene.freesound_data
        self.client.set_token(addon_data.freesound_api)
        s = self.client.check_access()
        if (s):
            addon_data.freesound_access = True
            return {'FINISHED'}
        else:
            addon_data.freesound_access = False
            return {'FINISHED'}

# Freesound Search
class Freesound_Search(bpy.types.Operator):
    bl_label = 'Search'
    bl_idname = 'freesound.search'
    bl_description = 'Search in Freesound archive'
    bl_options = {'REGISTER', 'UNDO'}
    client = freesound.FreesoundClient()
    def execute(self, context):
        addon_data = context.scene.freesound_data
        self.client.set_token(addon_data.freesound_api)
        s = self.client.check_access()
        if (s):
            addon_data.freesound_access = True
            return {'FINISHED'}
        else:
            addon_data.freesound_access = False
            return {'FINISHED'}

# Registration
def register():
    bpy.utils.register_module(__name__)

# Extend the scene class here to include the addon data
    bpy.types.Scene.freesound_data = bpy.props.PointerProperty(type=FreeSoundData)



def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == '__main__':
    register()
