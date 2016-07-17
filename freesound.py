import bpy.types
import os.path
import datetime
import aud
from . import freesound_api

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
    sound_is_playing = bpy.props.BoolProperty(
        description = 'Sound is playing'
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
    client = freesound_api.FreesoundClient()
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
    

# Freesound Add
class Freesound_Add(bpy.types.Operator):
    bl_label = 'Add'
    bl_idname = 'freesound.add'
    bl_description = 'Add sound to the timeline'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        addon_data = context.scene.freesound_data
        client = Freesound_Connect.get_client(Freesound_Connect)
        results_pager = client.text_search(query=addon_data.search_item,sort="rating_desc",fields="id,name,previews,username")
        for i in range(0, len(results_pager.results)):
            sound = results_pager[i]
            _sound = addon_data.freesound_list.add()
            _sound.name = sound.name
            _sound.author = sound.username


            print ("\t- " + sound.name + " by " + sound.username + sound.previews)

        return {'FINISHED'}
# Freesound Search
class Freesound_Search(bpy.types.Operator):
    bl_label = 'Search'
    bl_idname = 'freesound.search'
    bl_description = 'Search in Freesound archive'
    bl_options = {'REGISTER', 'UNDO'}
    results_pager = 0
    def execute(self, context):
        client = Freesound_Connect.get_client(Freesound_Connect)
        addon_data = context.scene.freesound_data
        Freesound_Search.results_pager = client.text_search(query=addon_data.search_item,sort="rating_desc",fields="id,name,previews,username,duration")
        addon_data.freesound_list.clear()
        for i in range(0, len(Freesound_Search.results_pager.results)):
            sound = Freesound_Search.results_pager[i]
            _sound = addon_data.freesound_list.add()
            _sound.sound_id = str(sound.id)
            _sound.duration = str(sound.duration)
            _sound.name = sound.name
            _sound.author = sound.username

            print ("\t- " + sound.name + " by " + sound.username)

        return {'FINISHED'}
    def get_results_pager(self):
        return self.results_pager
# Freesound Next page search
class Freesound_Next(bpy.types.Operator):
    bl_label = 'Next'
    bl_idname = 'freesound.nextpage'
    bl_description = 'Next page of sounds'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        addon_data = context.scene.freesound_data
        client = Freesound_Connect.get_client(Freesound_Connect)
        results_pager = Freesound_Search.results_pager
        addon_data.freesound_list.clear()
        results_pager = results_pager.next_page()
        Freesound_Search.results_pager = results_pager
        for i in range(0, len(results_pager.results)):
            sound = results_pager[i]
            _sound = addon_data.freesound_list.add()
            _sound.sound_id = str(sound.id)
            _sound.name = sound.name
            _sound.duration = str(sound.duration)
            _sound.author = sound.username
            print ("\t- " + sound.name + " by " + sound.username)

        return {'FINISHED'}
class FREESOUNDList(bpy.types.UIList):
    sound_id = 0
    def get_sound_id(self):
        return self.sound_id
    def draw_item(self,
                  context,
                  layout,
                  data,
                  item,
                  icon,
                  active_data,
                  active_propname
                  ):
        addon_data = context.scene.freesound_data
        sounds = addon_data.freesound_list
        split=layout.split(percentage=0.25)
        duration = str(datetime.timedelta(seconds=float(item.duration)))
        split.label(duration, icon="PLAY_AUDIO")
        split.label(item.name)
        split.label(item.author)
        FREESOUNDList.sound_id = addon_data.freesound_list[addon_data.active_list_item].sound_id
        print(FREESOUNDList.sound_id)

# Freesound Play
class Freesound_Play(bpy.types.Operator):
    bl_label = 'Play'
    bl_idname = 'freesound.play'
    bl_description = 'Preview the sound'
    bl_options = {'REGISTER', 'UNDO'}
    handle = 0
    def execute(self, context):
        addon_data = context.scene.freesound_data
        addon_data.sound_is_playing = True
        client = Freesound_Connect.get_client(Freesound_Connect)

        sound_id = FREESOUNDList.get_sound_id(FREESOUNDList)
        print (sound_id)
        sound_info = client.get_sound(sound_id)
        print (str(sound_info))
        preview_hq_file = str(sound_info.previews.preview_hq_mp3.split("/")[-1])
        #FIXME Store the file in Blender
        if (os.path.isfile('/tmp/' + preview_hq_file)):
            soundfile = '/tmp/' + preview_hq_file
        else:
            res = sound_info.retrieve_preview('/tmp')
            soundfile = res[0]

        device = aud.device()
        factory = aud.Factory(soundfile)
        Freesound_Play.handle = device.play(factory)
        Freesound_Play.handle.loop_count = -1

        return {'FINISHED'}

# Freesound Stop
class Freesound_Pause(bpy.types.Operator):
    bl_label = 'Pause'
    bl_idname = 'freesound.pause'
    bl_description = 'Pause the sound'
    bl_options = {'REGISTER', 'UNDO'}
    handle = 0
    def execute(self, context):
        addon_data = context.scene.freesound_data
        addon_data.sound_is_playing = False
        Freesound_Play.handle.stop()
        return {'FINISHED'}

