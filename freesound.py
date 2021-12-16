import os
import bpy
import bpy.types as btypes
from bpy.props import BoolProperty, StringProperty, FloatProperty, \
                      EnumProperty, IntProperty, CollectionProperty
import webbrowser
from os.path import dirname, realpath, isfile
from bpy import ops,context
import datetime, time
import aud
from . import freesound_api

# get addon preferences
def get_addon_preferences():
    addon = bpy.context.preferences.addons.get(__package__)
    return getattr(addon, "preferences", None)        
    
# create folder if needed
def create_folder(folderpath):
    if not os.path.isdir(folderpath):
        os.makedirs(folderpath, exist_ok=True)
    return folderpath


class FREESOUND_UL_List(btypes.UIList):
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
        # split=layout.split(factor=0.5, align=True)
        # try:
        #     duration = str(datetime.timedelta(seconds=float(item.duration)))
        # except:
        #     duration = "0"
        # split=layout.split(factor=0.2, align=True)
        # split.label(text=duration)
        layout.label(text=item.name)

        FREESOUND_UL_List.sound_id = addon_data.freesound_list[addon_data.active_list_item].sound_id
        FREESOUND_UL_List.avg_rating = addon_data.freesound_list[addon_data.active_list_item].avg_rating
        FREESOUND_UL_List.num_ratings = addon_data.freesound_list[addon_data.active_list_item].num_ratings
        FREESOUND_UL_List.comment = addon_data.freesound_list[addon_data.active_list_item].comment
        FREESOUND_UL_List.comments = addon_data.freesound_list[addon_data.active_list_item].comments

# Freesound Play
class Freesound_Play(btypes.Operator):
    bl_label = 'Play'
    bl_idname = 'freesound.play'
    bl_description = 'Preview the sound'
    bl_options = {'REGISTER', 'UNDO'}
    handle = 0
    def execute(self, context):
        addon_data = context.scene.freesound_data

        if (not addon_data.freesound_list_loaded):
            return {'FINISHED'}

        addon_data.sound_is_playing = True
        client = Freesound_Validate.get_client(Freesound_Validate)

        try:
            sound_id = FREESOUND_UL_List.get_sound_id(FREESOUND_UL_List)

            sound_info = client.get_sound(sound_id)
            
            if (addon_data.high_quality):
                preview_file = str(sound_info.previews.preview_hq_mp3.split("/")[-1])
            else:
                preview_file = str(sound_info.previews.preview_lq_mp3.split("/")[-1])

            if (preview_file):
                if (isfile(dirname(realpath(__file__)) + '/' + preview_file)):
                    soundfile = dirname(realpath(__file__)) + '/' + preview_file
                else:
                    soundfile = sound_info.retrieve_preview(dirname(realpath(__file__)),
                                                    sound_info.name,
                                                    addon_data.high_quality)
                # soundfile = sound filepath
                addon_data.soundfile = soundfile

            device = aud.Device()
            sound = aud.Sound.file(soundfile)
            Freesound_Play.handle = device.play(sound)
            Freesound_Play.handle.loop_count = -1
        except:
            print("[Play] Search something first...")
            return {'CANCELLED'}

        return {'FINISHED'}


class FreeSoundItem(btypes.PropertyGroup):
    sound_id: StringProperty(
        name="Sound ID",
        description="The ID of this sound",
        default="0"
    )
    avg_rating: FloatProperty(
        name="Average Rating",
        description="Numerical average rating",
        default=0
    )
    num_ratings: StringProperty(
        name="Number of Ratings",
        description="Ratings",
        default="0"
    )
    comment: StringProperty(
        name="Comment",
        description="Comment",
        default="0"
    )
    comments: StringProperty(
        name="Comments",
        description="Comments",
        default="0"
    )
    play: BoolProperty()
    add : BoolProperty()
    duration : StringProperty(
        name="Sound Duration",
        description="Duration of sound",
        default="NaN"
    )
    name: StringProperty(
        name="Sound name",
        description="The name of this sound",
        default="Name"
    )
    author: StringProperty(
        name="Author",
        description="The author of this sound",
        default="Author"
    )

    @classmethod
    def poll(cls, context):
        return context.scene.freesound_data.active_list_item


# Definess one instance of the addon data (one per scene)
class FreeSoundData(btypes.PropertyGroup):
    def update_max(self, context):

        value = context.scene.freesound_data.current_page
        if (value > 1):
            if (context.scene.freesound_data.current_page > value):
                context.scene.freesound_data.current_page = value
            ops.freesound.current_page(context.scene.freesound_data.current_page)
        return None

    high_quality: BoolProperty(
        name="HQ",
        description="Best quality play and add for non-oauth2"
    )
    duration_from: FloatProperty(
        description = "Insert duration in seconds. -1 means any",
        default=-1,
        min=-1,
        precision=1
    )
    duration_to: FloatProperty(
        description = "Insert duration in seconds. -1 means any",
        default=-1,
        min=-1,
        precision=1
    )
    search_filter: EnumProperty(
        items = [
            ('score_desc', 'Automatic by relevance', 'Automatic by relevance'),
            ('rating_desc', 'Rating (Highest)', 'Rating (Highest)'),
            ('rating_asc', 'Rating (Lowest)', 'Rating (Lowest)'),
            ('duration_desc', 'Duration (long first)', 'Duration (long first)'),
            ('duration_asc', 'Duration (short first)', 'Duration (short first)')
        ],
        name="",
        default="score_desc",
        description="Order"
    )
    license: EnumProperty(
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

    download_location: EnumProperty(
        items = [
            ('PROJECT', 'Alongside Project', 'Alongside Project'),
            ('COMMON', 'Common Folder', 'Common Folder'),
        ],
        name="Download Location",
        default='PROJECT',
        description="Where to store downloaded sound files"
    )

    current_page: IntProperty(
        description = "Current Pager",
        default=1,
        min=1,
        update=update_max
    )
    pager_num: IntProperty(
        description = "Current pager",
        default = 0
    )
    sounds: IntProperty(
        description = "Number of sounds",
        default = 0
    )
    soundfile: StringProperty(
        name="Sound Path",
        description="Path to the file",
        default=dirname(realpath(__file__))
    )
    sound_is_playing: BoolProperty(
        description = 'Sound is playing'
    )
    freesound_loading: BoolProperty(
        description = 'Loading'
    )
    freesound_access: BoolProperty(
        description=(
            'Access to Freesound API'
        )
    )
    search_item: StringProperty(
        description=(
            'Sound to search'
        )
    )
    active_list_item: IntProperty()
    freesound_list: CollectionProperty(type=FreeSoundItem)
    freesound_list_loaded: BoolProperty()


class Freesound_Page(btypes.Operator):
    bl_label = "Jump to Page"
    bl_idname = "freesound.current_page"

    def execute(self, context):
        if (context.scene.freesound_data.freesound_list_loaded):
            addon_data = context.scene.freesound_data
            try:
                pages = int(addon_data.sounds/len(addon_data.freesound_list))
            except:
                pages = 0
            if (addon_data.current_page > 1 and addon_data.current_page < pages):
                results_pager = Freesound_Search.results_pager
                Freesound_Search.results_pager = results_pager.get_page(addon_data.current_page)
                addon_data.freesound_list.clear()

                for i in range(0, len(Freesound_Search.results_pager.results)):
                    sound = Freesound_Search.results_pager[i]
                    _sound = addon_data.freesound_list.add()
                    _sound.sound_id = str(sound.id)
                    _sound.name = str(sound.name)
                    _sound.avg_rating = sound.avg_rating
                    _sound.duration = str(sound.duration)
                    _sound.author = str(sound.username)
                Freesound_Search.results_pager = results_pager

        else:
            print ("Nothing in search")

        return {'FINISHED'}

# Freesound Validate
class Freesound_Validate(btypes.Operator):
    bl_label = 'Validate'
    bl_idname = 'freesound.validate'
    bl_description = 'Validate API for Freesound'
    bl_options = {'REGISTER', 'UNDO'}
    client = freesound_api.FreesoundClient()
    def get_client(self):
        return self.client
    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        self.client.set_token(addon_prefs.freesound_api)
        s = self.client.check_access()
        if (s):
            addon_prefs.freesound_access = True
            return {'FINISHED'}
        else:
            addon_prefs.freesound_access = False
            return {'FINISHED'}

# Freesound Info
class Freesound_Info(btypes.Operator):
    bl_label = 'Info'
    bl_idname = 'freesound.info'
    bl_description = 'Information about the user and sound'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        try:
            addon_data = context.scene.freesound_data
            sound_id = FREESOUND_UL_List.get_sound_id(FREESOUND_UL_List)
            client = Freesound_Validate.get_client(Freesound_Validate)
            sound_info = client.get_sound(sound_id)
            user = sound_info.username
            url = 'https://www.freesound.org/people/'+ user  + '/sounds/'  + str(sound_id)
            webbrowser.open(url)
        except:
            print ("[Info] Search something first...")

        return {'FINISHED'}


# Freesound Add
class Freesound_Add(btypes.Operator):
    bl_label = 'Add'
    bl_idname = 'freesound.add'
    bl_description = 'Add sound to the VSE at current frame'
    bl_options = {'REGISTER', 'UNDO'}

    # poll out if project location and not saved

    def execute(self, context):
        prefs = get_addon_preferences()
        addon_data = context.scene.freesound_data
        if (not addon_data.freesound_list_loaded):
            return {'FINISHED'}

        sound_id = FREESOUND_UL_List.get_sound_id(FREESOUND_UL_List)
        client = Freesound_Validate.get_client(Freesound_Validate)
        sound_info = client.get_sound(sound_id)

        if (addon_data.high_quality):
            preview_file = str(sound_info.previews.preview_hq_mp3.split("/")[-1])
        else:
            preview_file = str(sound_info.previews.preview_lq_mp3.split("/")[-1])

        # build filepath
        if addon_data.download_location=="PROJECT":
            if prefs.freesound_project_folder_pattern != "":
                blend_folder = os.path.dirname(bpy.data.filepath)
                freesound_folder = os.path.join(blend_folder, prefs.freesound_project_folder_pattern)
                sound_filepath = os.path.join(freesound_folder, preview_file)
            else:
                self.report({'WARNING'}, 'No folder pattern specified, check addon preferences')
                return {'FINISHED'}
        else:
            # create dir if needed
            freesound_folder = prefs.freesound_download_folderpath
            sound_filepath = os.path.join(freesound_folder, preview_file)

        if (isfile(dirname(realpath(__file__)) + '/' + preview_file)):
            soundfile = dirname(realpath(__file__)) + '/' + preview_file
        else:
            soundfile = sound_info.retrieve_preview(dirname(realpath(__file__)),
                                            sound_info.name,
                                            addon_data.high_quality)
        addon_data.soundfile = soundfile
        # soundfile = sound filepath

        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()
        scn = bpy.context.scene
        seq = scn.sequence_editor
        cf = scn.frame_current
        sequences = bpy.context.sequences

        if not sequences:
            addSceneChannel = 1
        else:
            channels = [s.channel for s in sequences]
            channels = sorted(list(set(channels)))
            empty_channel = channels[-1] + 1
            addSceneChannel = empty_channel

        name = os.path.basename(addon_data.soundfile)
        newStrip = seq.sequences.new_sound(name=name, filepath=addon_data.soundfile, \
                                    channel=addSceneChannel, frame_start=cf)
        seq.sequences_all[newStrip.name].frame_start = cf
        return {'FINISHED'}

# Freesound Search
class Freesound_Search(btypes.Operator):
    bl_label = 'Search'
    bl_idname = 'freesound.search'
    bl_description = 'Search in Freesound archive'
    bl_options = {'REGISTER', 'UNDO'}
    results_pager = 0
    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences
        client = Freesound_Validate.get_client(Freesound_Validate)

        if (not client.token):
            ops.freesound.validate()

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

        rating = addon_data.search_filter
        Freesound_Search.results_pager = client.text_search(query=addon_data.search_item,filter=filter_string, sort=rating,fields="id,name,previews,username,duration,avg_rating,num_ratings,comment,comments")
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

        if len(addon_data.freesound_list) > 0:
            addon_data.freesound_list_loaded = True
            bpy.ops.freesound.firstpage()
        else:
            addon_data.freesound_list_loaded = False
        return {'FINISHED'}
    def get_results_pager(self):
        return self.results_pager

# Freesound Next page search
class Freesound_Next(btypes.Operator):
    bl_label = 'Next'
    bl_idname = 'freesound.nextpage'
    bl_description = 'Next page of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_data = context.scene.freesound_data
        try:
            pages = int(addon_data.sounds/len(addon_data.freesound_list))
        except:
            return {'FINISHED'}
        if (addon_data.current_page > pages):
            return {'FINISHED'}

        if (addon_data.freesound_list_loaded):
            results_pager = Freesound_Search.results_pager

            if (addon_data.current_page < pages):
                addon_data.freesound_list.clear()
                Freesound_Search.results_pager = results_pager.next_page()

                for i in range(0, len(Freesound_Search.results_pager.results)):
                    sound = Freesound_Search.results_pager[i]
                    _sound = addon_data.freesound_list.add()
                    _sound.sound_id = str(sound.id)
                    _sound.name = str(sound.name)
                    _sound.avg_rating = sound.avg_rating
                    _sound.duration = str(sound.duration)
                    _sound.author = str(sound.username)

                addon_data.current_page += 1

        return {'FINISHED'}

# Freesound Next 10 pages search
class Freesound_Next10(btypes.Operator):
    bl_label = 'Next 10'
    bl_idname = 'freesound.next10page'
    bl_description = 'Next 10 pages of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_data = context.scene.freesound_data
        try:
            pages = int(addon_data.sounds/len(addon_data.freesound_list))
        except:
            return {'FINISHED'}
        addon_data.current_page += 10
        if (addon_data.current_page > pages):
            addon_data.current_page -= 10
            return {'FINISHED'}

        if (addon_data.freesound_list_loaded):
            results_pager = Freesound_Search.results_pager
            if (addon_data.current_page < pages):
                addon_data.freesound_list.clear()
                Freesound_Search.results_pager = results_pager.get_page(addon_data.current_page)

                for i in range(0, len(Freesound_Search.results_pager.results)):
                    sound = Freesound_Search.results_pager[i]
                    _sound = addon_data.freesound_list.add()
                    _sound.sound_id = str(sound.id)
                    _sound.name = str(sound.name)
                    _sound.avg_rating = sound.avg_rating
                    _sound.duration = str(sound.duration)
                    _sound.author = str(sound.username)
        return {'FINISHED'}

# Freesound Last page search
class Freesound_Last(btypes.Operator):
    bl_label = 'Last'
    bl_idname = 'freesound.lastpage'
    bl_description = 'Last page of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_data = context.scene.freesound_data
        if (addon_data.freesound_list_loaded):
            results_pager = Freesound_Search.results_pager
            addon_data.pager_num = int(addon_data.sounds/len(addon_data.freesound_list))

            addon_data.freesound_list.clear()
            Freesound_Search.results_pager = results_pager.get_page(addon_data.pager_num)

            for i in range(0, len(Freesound_Search.results_pager.results)):
                sound = Freesound_Search.results_pager[i]
                _sound = addon_data.freesound_list.add()
                _sound.sound_id = str(sound.id)
                _sound.name = str(sound.name)
                _sound.avg_rating = sound.avg_rating
                _sound.duration = str(sound.duration)
                _sound.author = str(sound.username)
            addon_data.current_page = addon_data.pager_num

        return {'FINISHED'}

# Freesound Prev page search
class Freesound_Prev(btypes.Operator):
    bl_label = 'Prev'
    bl_idname = 'freesound.prevpage'
    bl_description = 'Prev page of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_data = context.scene.freesound_data
        cur_page = addon_data.current_page - 1
        if (cur_page == 0):
            addon_data.current_page = 1
            return {'FINISHED'}

        if (addon_data.freesound_list_loaded):
            results_pager = Freesound_Search.results_pager

            addon_data.freesound_list.clear()
            Freesound_Search.results_pager = results_pager.previous_page()

            for i in range(0, len(Freesound_Search.results_pager.results)):
                sound = Freesound_Search.results_pager[i]
                _sound = addon_data.freesound_list.add()
                _sound.sound_id = str(sound.id)
                _sound.name = sound.name
                _sound.avg_rating = sound.avg_rating
                _sound.duration = str(sound.duration)
                _sound.author = sound.username
            addon_data.current_page -= 1
        return {'FINISHED'}

# Freesound Prev 10 pages search
class Freesound_Prev10(btypes.Operator):
    bl_label = 'Next 10'
    bl_idname = 'freesound.prev10page'
    bl_description = 'Prev 10 pages of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_data = context.scene.freesound_data
        cur_page = addon_data.current_page - 10
        if (cur_page <= 0):
            addon_data.current_page = 1
            return {'FINISHED'}
        if (addon_data.freesound_list_loaded):
            results_pager = Freesound_Search.results_pager

            addon_data.freesound_list.clear()
            Freesound_Search.results_pager = results_pager.get_page(addon_data.current_page - 10)

            for i in range(0, len(Freesound_Search.results_pager.results)):
                sound = Freesound_Search.results_pager[i]
                _sound = addon_data.freesound_list.add()
                _sound.sound_id = str(sound.id)
                _sound.name = str(sound.name)
                _sound.avg_rating = sound.avg_rating
                _sound.duration = str(sound.duration)
                _sound.author = str(sound.username)
            addon_data.current_page -= 10
        return {'FINISHED'}

# Freesound First page search
class Freesound_First(btypes.Operator):
    bl_label = 'First'
    bl_idname = 'freesound.firstpage'
    bl_description = 'First page of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_data = context.scene.freesound_data
        if (addon_data.freesound_list_loaded):
            results_pager = Freesound_Search.results_pager
            addon_data.pager_num = int(addon_data.sounds/len(addon_data.freesound_list))
            addon_data.freesound_list.clear()
            Freesound_Search.results_pager = results_pager.get_page(1)

            for i in range(0, len(Freesound_Search.results_pager.results)):
                sound = Freesound_Search.results_pager[i]
                _sound = addon_data.freesound_list.add()
                _sound.sound_id = str(sound.id)
                _sound.name = str(sound.name)
                _sound.avg_rating = sound.avg_rating
                _sound.duration = str(sound.duration)
                _sound.author = str(sound.username)
            addon_data.current_page = 1

        return {'FINISHED'}
# Freesound Stop
class Freesound_Pause(btypes.Operator):
    bl_label = 'Pause'
    bl_idname = 'freesound.pause'
    bl_description = 'Pause the sound'
    bl_options = {'REGISTER', 'UNDO'}
    handle = 0
    def execute(self, context):
        addon_data = context.scene.freesound_data
        if (addon_data.freesound_list_loaded):
            addon_data.sound_is_playing = False
            Freesound_Play.handle.stop()
        return {'FINISHED'}

