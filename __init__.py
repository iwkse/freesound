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
    sound_id = bpy.props.StringProperty(
        name="Sound ID",
        description="The ID of this sound",
        default="0"
    )
    duration = bpy.props.StringProperty(
        name="Sound Duration",
        description="Duration of sound",
        default="NaN"
    )
    name = bpy.props.StringProperty(
        name="Sound name",
        description="The name of this sound",
        default="Name"
    )
    author = bpy.props.StringProperty(
        name="Author",
        description="The author of this sound",
        default="Author"
    )
    @classmethod
    def poll(cls, context):
        return context.scene.freesound_data.active_list_item

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


    
# Freesound Connect
class Freesound_Connect(bpy.types.Operator):
    bl_label = 'Connect'
    bl_idname = 'freesound.connect'
    bl_description = 'Connect to Freesound'
    bl_options = {'REGISTER', 'UNDO'}
    client = freesound.FreesoundClient()
    def get_client(self):
        return self.client
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

# Freesound Play
class Freesound_Play(bpy.types.Operator):
    bl_label = 'Play'
    bl_idname = 'freesound.play'
    bl_description = 'Preview the sound'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        addon_data = context.scene.freesound_data
        client = Freesound_Connect.get_client(Freesound_Connect)

        sound_info = client.get_sound(addon_data.active_sound_id)
        print (sound_info)

        return {'FINISHED'}
# Freesound Add
class Freesound_Add(bpy.types.Operator):
    bl_label = 'Add'
    bl_idname = 'freesound.add'
    bl_description = 'Add sound to the timeline'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        addon_data = context.scene.freesound_data
        client = super(Freesound_Connect).client
        results_pager = client.text_search(query=addon_data.search_item,sort="rating_desc",fields="id,name,previews,username")
        for i in range(0, len(results_pager.results)):
            sound = results_pager[i]
            _sound = addon_data.freesound_list.add()
            _sound.name = sound.name
            _sound.author = sound.username


            print ("\t- " + sound.name + " by " + sound.username)

        return {'FINISHED'}
# Freesound Search
class Freesound_Search(bpy.types.Operator):
    bl_label = 'Search'
    bl_idname = 'freesound.search'
    bl_description = 'Search in Freesound archive'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        client = Freesound_Connect.get_client(Freesound_Connect)
        addon_data = context.scene.freesound_data
        results_pager = client.text_search(query=addon_data.search_item,sort="rating_desc",fields="id,name,previews,username,duration")
        addon_data.freesound_list.clear()
        for i in range(0, len(results_pager.results)):
            sound = results_pager[i]
            _sound = addon_data.freesound_list.add()
            _sound.sound_id = str(sound.id)
            _sound.duration = str(sound.duration)
            _sound.name = sound.name
            _sound.author = sound.username


            print ("\t- " + sound.name + " by " + sound.username)

        return {'FINISHED'}
# Freesound Next page search
class Freesound_Next(bpy.types.Operator):
    bl_label = 'Next'
    bl_idname = 'freesound.nextpage'
    bl_description = 'Next page of sounds'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        addon_data = context.scene.freesound_data
        client = super(Freesound_Connect).client
        results_pager = client.results_pager.next_page()
        addon_data.freesound_list.clear()
        for i in range(0, len(results_pager.results)):
            sound = results_pager[i]
            _sound = addon_data.freesound_list.add()
            _sound.name = sound.name
            _sound.author = sound.username
            print ("\t- " + sound.name + " by " + sound.username)

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
