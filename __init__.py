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
    "description": "Connect to http://freesound.org for goodies",
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
