import bpy.types
import webbrowser
import os.path
import datetime
import aud
from . import freesound_api


class FREESOUNDList(bpy.types.UIList):
    sound_id = 0
    avg_rating = 0
    num_ratings = 0
    comment = 0
    comments = 0

    def get_sound_id(self):
        return self.sound_id
    def get_avg_rating(self):
        return self.avg_rating
    def get_num_rating(self):
        return self.num_rating
    def get_comment(self):
        return self.comment
    def get_comments(self):
        return self.comments

    def draw_item(self,
                  context,
                  layout,
                  data,
                  item,
                  icon,
                  active_data,
                  active_propname
                  ):
        obj = active_data
        addon_data = context.scene.freesound_data
        sounds = addon_data.freesound_list
        split=layout.split(percentage=0.5)
        try:
            duration = str(datetime.timedelta(seconds=float(item.duration)))
        except:
            duration = "0"
        split=layout.split(percentage=0.2)
        split.label(duration)
        split.label(item.name)

        FREESOUNDList.sound_id = addon_data.freesound_list[addon_data.active_list_item].sound_id
        FREESOUNDList.avg_rating = addon_data.freesound_list[addon_data.active_list_item].avg_rating
        FREESOUNDList.num_ratings = addon_data.freesound_list[addon_data.active_list_item].num_ratings
        FREESOUNDList.comment = addon_data.freesound_list[addon_data.active_list_item].comment
        FREESOUNDList.comments = addon_data.freesound_list[addon_data.active_list_item].comments

# Freesound Play
class Freesound_Play(bpy.types.Operator):
    bl_label = 'Play'
    bl_idname = 'freesound.play'
    bl_description = 'Preview the sound'
    bl_options = {'REGISTER', 'UNDO'}
    handle = 0
    def execute(self, context):
        addon_data = context.scene.freesound_data

        if (not addon_data.freesound_list_loaded):  
            return {"FINISHED"}

        try:
            addon_data.sound_is_playing = True
            client = Freesound_Validate.get_client(Freesound_Validate)

            sound_id = FREESOUNDList.get_sound_id(FREESOUNDList)
            sound_info = client.get_sound(sound_id)
            if (addon_data.high_quality):
                preview_file = str(sound_info.previews.preview_hq_mp3.split("/")[-1])
            else:
                preview_file = str(sound_info.previews.preview_lq_mp3.split("/")[-1])

            if (preview_file):
                if (os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + '/' + preview_file)):
                    soundfile = os.path.dirname(os.path.realpath(__file__)) + '/' + preview_file
                else:
                    res = sound_info.retrieve_preview(os.path.dirname(os.path.realpath(__file__)), addon_data.high_quality)
                    soundfile = res[0]
                addon_data.soundfile = soundfile
                device = aud.device()
                factory = aud.Factory(soundfile)
                Freesound_Play.handle = device.play(factory)
                Freesound_Play.handle.loop_count = -1
        except:
            print ("File not found, search first")
        return {'FINISHED'}


class FreeSoundItem(bpy.types.PropertyGroup):
    sound_id = bpy.props.StringProperty(
        name="Sound ID",
        description="The ID of this sound",
        default="0"
    )
    avg_rating = bpy.props.FloatProperty(
        name="Average Rating",
        description="Numerical average rating",
        default=0
    )
    num_ratings = bpy.props.StringProperty(
        name="Number of Ratings",
        description="Ratings",
        default="0"
    )
    comment = bpy.props.StringProperty(
        name="Comment",
        description="Comment",
        default="0"
    )
    comments = bpy.props.StringProperty(
        name="Comments",
        description="Comments",
        default="0"
    )
    play = bpy.props.BoolProperty()
    add = bpy.props.BoolProperty()
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
# Definess one instance of the addon data (one per scene)
class FreeSoundData(bpy.types.PropertyGroup):
    high_quality = bpy.props.BoolProperty(
        name="HQ",
        description="Best quality play and add for non-oauth2"
    )
    duration_from = bpy.props.FloatProperty(
        description = "Insert duration in seconds. -1 means any",
        default=-1,
        min=-1,
        precision=1
    )
    current_page = bpy.props.FloatProperty(
        description = "Current Pager",
        default=1,
        min=1,
        precision=0
    )
    duration_to = bpy.props.FloatProperty(
        description = "Insert duration in secondsi. -1 means any",
        default=-1,
        min=-1,
        precision=1
    )
    license = bpy.props.EnumProperty(
        items = [
            ('ALL', 'All', 'All'),
            ('Attribution', 'Attribution', 'Attribution'),
            ('Attribution Noncommercial', 'Attribution Noncommercial', 'Attribution Noncommercial'),
            ('Creative Commons 0', 'Creative Commons 0', 'Creative Commons 0'),
            ('Sampling+', 'Sampling+', 'Sampling+')
        ],
        name="",
        default='ALL',
        description="The type of license"
    )
    pager_num = bpy.props.IntProperty(
        description = "Current pager",
        default = 0
    )
    sounds = bpy.props.IntProperty(
        description = "Number of sounds",
        default = 0
    )
    soundfile = bpy.props.StringProperty(
        name="Sound Path",
        description="Path to the file",
        default=os.path.dirname(os.path.realpath(__file__))
    )
    sound_is_playing = bpy.props.BoolProperty(
        description = 'Sound is playing'
    )
    freesound_loading = bpy.props.BoolProperty(
        description = 'Loading'
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
    freesound_list_loaded = bpy.props.BoolProperty()

# Freesound Validate
class Freesound_Validate(bpy.types.Operator):
    bl_label = 'Validate'
    bl_idname = 'freesound.validate'
    bl_description = 'Validate API for Freesound'
    bl_options = {'REGISTER', 'UNDO'}
    client = freesound_api.FreesoundClient()
    def get_client(self):
        return self.client
    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        print ("Validate: " + addon_prefs.freesound_api)
        self.client.set_token(addon_prefs.freesound_api)
        s = self.client.check_access()
        if (s):
            addon_prefs.freesound_access = True
            return {'FINISHED'}
        else:
            addon_prefs.freesound_access = False
            return {'FINISHED'}

# Freesound Info
class Freesound_Info(bpy.types.Operator):
    bl_label = 'Info'
    bl_idname = 'freesound.info'
    bl_description = 'Add sound to the VSE at current frame'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        try:
            addon_data = context.scene.freesound_data
            sound_id = FREESOUNDList.get_sound_id(FREESOUNDList)
            sound_id.username
            client = Freesound_Validate.get_client(Freesound_Validate)
            sound_info = client.get_sound(sound_id)
            user = sound_info.username
            url = 'https://www.freesound.org/people/'+ user  + '/sounds/'  + str(sound_info.id)
            webbrowser.open(url)
        except:
            print ("File not found, search first")
        
        return {'FINISHED'}
# Freesound Add
class Freesound_Add(bpy.types.Operator):
    bl_label = 'Add'
    bl_idname = 'freesound.add'
    bl_description = 'Add sound to the VSE at current frame'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        try:
            addon_data = context.scene.freesound_data
            sound_id = FREESOUNDList.get_sound_id(FREESOUNDList)
            client = Freesound_Validate.get_client(Freesound_Validate)
            sound_info = client.get_sound(sound_id)
            if (addon_data.high_quality):
                preview_file = str(sound_info.previews.preview_hq_mp3.split("/")[-1])
            else:
                preview_file = str(sound_info.previews.preview_lq_mp3.split("/")[-1])
            
            if (os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + '/' + preview_file)):
                soundfile = os.path.dirname(os.path.realpath(__file__)) + '/' + preview_file
            else:
                res = sound_info.retrieve_preview(os.path.dirname(os.path.realpath(__file__)), addon_data.high_quality)
                soundfile = res[0]
            addon_data.soundfile = soundfile
            bpy.ops.sequencer.sound_strip_add(filepath=addon_data.soundfile, frame_start=bpy.context.scene.frame_current)
        except:
            print ("File not found, search first")

        return {'FINISHED'}
    
# Freesound Search
class Freesound_Search(bpy.types.Operator):
    bl_label = 'Search'
    bl_idname = 'freesound.search'
    bl_description = 'Search in Freesound archive'
    bl_options = {'REGISTER', 'UNDO'}
    results_pager = 0
    def execute(self, context):
        addon_prefs = context.user_preferences.addons[__package__].preferences
        client = Freesound_Validate.get_client(Freesound_Validate)
        
        if (not client.token):
            bpy.ops.freesound.validate()

        addon_data = context.scene.freesound_data
        addon_data.freesound_loading = True
        try:
            int(addon_data.duration_from)
        except:
            addon_data.duration_from = "-1"

        try:
            int(addon_data.duration_to)
        except:
            addon_data.duration_to = "-1"
        
        if (addon_data.duration_from == -1):
            duration_from = "*"
        else:
            duration_from = str(addon_data.duration_from)
        if (addon_data.duration_to == -1):
            duration_to = "*"
        else:
            duration_to = str(addon_data.duration_to)

        duration = "duration:[" + duration_from + " TO " + duration_to + "]"

        if (addon_data.license != 'ALL'):
            filter_string=duration + ' license:"' + addon_data.license + '"'
        else:
            filter_string=duration
        Freesound_Search.results_pager = client.text_search(query=addon_data.search_item,filter=filter_string, sort="rating_desc",fields="id,name,previews,username,duration,avg_rating,num_ratings,comment,comments")
        addon_data.freesound_list.clear()
        addon_data.sounds = Freesound_Search.results_pager.count
        for i in range(0, len(Freesound_Search.results_pager.results)):
            sound = Freesound_Search.results_pager[i]
            _sound = addon_data.freesound_list.add()
            _sound.sound_id = str(sound.id)
            _sound.avg_rating = sound.avg_rating
            _sound.num_ratings = str(sound.num_ratings)
            _sound.comment = sound.comment
            _sound.comments = sound.comments
            _sound.duration = str(sound.duration)
            _sound.name = sound.name
            _sound.author = sound.username

        addon_data.freesound_list_loaded = True
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
        client = Freesound_Validate.get_client(Freesound_Validate)
        results_pager = Freesound_Search.results_pager
        addon_data.pager_num += 1 

        if (addon_data.pager_num == results_pager.results):
            addon_data.pager_num -= 1 
            return {'FINISHED'}
        
        addon_data.freesound_list.clear()
        Freesound_Search.results_pager = results_pager.next_page()

        for i in range(0, len(Freesound_Search.results_pager.results)):
            sound = Freesound_Search.results_pager[i]
            _sound = addon_data.freesound_list.add()
            _sound.sound_id = str(sound.id)
            _sound.name = str(sound.name)
            _sound.duration = str(sound.duration)
            _sound.author = str(sound.username)
        addon_data.current_page += 1 
        return {'FINISHED'}

# Freesound Prev page search
class Freesound_Prev(bpy.types.Operator):
    bl_label = 'Prev'
    bl_idname = 'freesound.prevpage'
    bl_description = 'Next page of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_data = context.scene.freesound_data
        client = Freesound_Validate.get_client(Freesound_Validate)
        results_pager = Freesound_Search.results_pager
        addon_data.pager_num -= 1 
        if (addon_data.pager_num < 0):
            addon_data.pager_num += 1 
            return {'FINISHED'}
        
        addon_data.freesound_list.clear()
        Freesound_Search.results_pager = results_pager.previous_page()

        for i in range(0, len(Freesound_Search.results_pager.results)):
            sound = Freesound_Search.results_pager[i]
            _sound = addon_data.freesound_list.add()
            _sound.sound_id = str(sound.id)
            _sound.name = sound.name
            _sound.duration = str(sound.duration)
            _sound.author = sound.username
        addon_data.current_page -= 1 
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

