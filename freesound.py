import os
import re
import math
import bpy
import bpy.types as btypes
from bpy.props import BoolProperty, StringProperty, FloatProperty, \
                      EnumProperty, IntProperty, CollectionProperty
import webbrowser
from os.path import dirname, isfile, isdir, join
from urllib.parse import quote
import aud
from . import freesound_api

# Highest channel available in the sequencer
MAX_CHANNEL = 128

def create_folder(folderpath):
    if not isdir(folderpath):
        os.makedirs(folderpath, exist_ok=True)
    return folderpath

def build_download_filepath(download_location, prefs, file_name):
    if download_location=="PROJECT":
        if prefs.freesound_project_folder_pattern == "":
            return "pattern_missing"
        elif not bpy.data.is_saved:
            return "blend_not_saved"
        else:
            blend_folder = dirname(bpy.data.filepath)
            freesound_folder = create_folder(join(blend_folder, prefs.freesound_project_folder_pattern))
            sound_filepath = join(freesound_folder, file_name)
    else:
        freesound_folder = create_folder(bpy.path.abspath(prefs.freesound_download_folderpath))
        sound_filepath = join(freesound_folder, file_name)

    return sound_filepath

def preview_file_name(item, high_quality):
    # Sound id and quality keep different sounds with the same name, and the
    # HQ/LQ previews of the same sound, from overwriting each other
    name = re.sub(r'[^\w\-. ]', '_', os.path.splitext(item.name)[0]).strip()
    return "%s_%s_%s.mp3" % (item.sound_id,
                             "hq" if high_quality else "lq",
                             name[:80] or "sound")

def get_active_item(addon_data):
    if not addon_data.freesound_list_loaded:
        return None
    index = addon_data.active_list_item
    if 0 <= index < len(addon_data.freesound_list):
        return addon_data.freesound_list[index]
    return None

def online_access_error():
    """Return an error message when Blender is not allowed to go online (Blender 4.2+)."""
    if getattr(bpy.app, "online_access", True):
        return None
    if getattr(bpy.app, "online_access_override", False):
        return 'Online access is disabled from the command line'
    return 'Online access is disabled, enable it in Preferences > System > Network'

def get_client(context):
    client = Freesound_Validate.client
    if not client.token:
        prefs = context.preferences.addons[__package__].preferences
        client.set_token(prefs.freesound_api)
    return client

def error_message(error):
    if isinstance(error, freesound_api.FreesoundException):
        detail = error.detail
        if isinstance(detail, dict):
            detail = detail.get("detail", detail)
        return "Freesound error %s: %s" % (error.code, detail)
    return "%s: %s" % (type(error).__name__, error)

def page_count(addon_data):
    if addon_data.page_size <= 0:
        return 1
    return max(1, int(math.ceil(addon_data.sounds / addon_data.page_size)))

def fill_list(addon_data, pager):
    addon_data.freesound_list.clear()
    for i in range(0, len(pager.results)):
        sound = pager[i]
        _sound = addon_data.freesound_list.add()
        _sound.sound_id = str(sound.id)
        _sound.name = str(sound.name)
        _sound.avg_rating = getattr(sound, "avg_rating", 0) or 0
        _sound.num_ratings = str(getattr(sound, "num_ratings", 0))
        _sound.comment = str(getattr(sound, "comment", "") or "")
        _sound.comments = str(getattr(sound, "comments", "") or "")
        _sound.duration = str(getattr(sound, "duration", "NaN"))
        _sound.author = str(sound.username)
    addon_data.active_list_item = 0
    addon_data.freesound_list_loaded = len(addon_data.freesound_list) > 0

# Set while the add-on itself changes current_page, so the update callback
# does not fetch the page a second time
_setting_page = False

def set_current_page(addon_data, page):
    global _setting_page
    _setting_page = True
    try:
        addon_data.current_page = page
    finally:
        _setting_page = False

def go_to_page(addon_data, page):
    """Load result page number `page` (clamped to the valid range)."""
    pager = Freesound_Search.results_pager
    if not addon_data.freesound_list_loaded or not pager:
        return
    page = min(max(1, page), page_count(addon_data))
    pager = pager.get_page(page)
    Freesound_Search.results_pager = pager
    fill_list(addon_data, pager)
    set_current_page(addon_data, page)

def run_page_change(operator, context, page):
    offline = online_access_error()
    if offline:
        operator.report({'WARNING'}, offline)
        return {'CANCELLED'}
    try:
        go_to_page(context.scene.freesound_data, page)
    except Exception as e:
        operator.report({'WARNING'}, error_message(e))
        return {'CANCELLED'}
    return {'FINISHED'}

def get_preview(operator, context, location):
    """Return the local path of the active sound preview, downloading it if needed."""
    addon_data = context.scene.freesound_data
    item = get_active_item(addon_data)
    if item is None:
        operator.report({'WARNING'}, 'Search and select a sound first')
        return None

    sound_filepath = build_download_filepath(
        location,
        context.preferences.addons[__package__].preferences,
        preview_file_name(item, addon_data.high_quality)
    )
    if sound_filepath == "blend_not_saved":
        operator.report({'WARNING'}, 'Blend file not saved, unable to store file alongside project')
        return None
    elif sound_filepath == "pattern_missing":
        operator.report({'WARNING'}, 'No folder pattern specified, check addon preferences')
        return None

    if not isfile(sound_filepath):
        offline = online_access_error()
        if offline:
            operator.report({'WARNING'}, offline)
            return None
        print("Freesound Addon --- Downloading File : %s" % item.name)
        try:
            sound_info = get_client(context).get_sound(item.sound_id)
            sound_filepath = sound_info.retrieve_preview(dirname(sound_filepath),
                                                         os.path.basename(sound_filepath),
                                                         addon_data.high_quality)
        except Exception as e:
            operator.report({'WARNING'}, 'Download failed. ' + error_message(e))
            return None

    addon_data.soundfile = sound_filepath
    return sound_filepath

class FREESOUND_UL_List(btypes.UIList):
    def draw_item(self,
                  context,
                  layout,
                  data,
                  item,
                  icon,
                  active_data,
                  active_propname
                  ):
        layout.label(text=item.name)

# Freesound Play
class Freesound_Play(btypes.Operator):
    bl_label = 'Play'
    bl_idname = 'freesound.play'
    bl_description = 'Preview the sound'
    bl_options = {'REGISTER', 'UNDO'}
    handle = None
    def execute(self, context):
        addon_data = context.scene.freesound_data

        sound_filepath = get_preview(self, context, addon_data.preview_location)
        if sound_filepath is None:
            return {'CANCELLED'}

        try:
            stop_playback()
            print("Freesound Addon --- Playing File : %s" % sound_filepath)
            device = aud.Device()
            sound = aud.Sound.file(sound_filepath)
            Freesound_Play.handle = device.play(sound)
            Freesound_Play.handle.loop_count = -1
        except Exception as e:
            self.report({'WARNING'}, 'Playback failed. ' + error_message(e))
            return {'CANCELLED'}

        addon_data.sound_is_playing = True
        return {'FINISHED'}

def stop_playback():
    handle = Freesound_Play.handle
    Freesound_Play.handle = None
    if handle is not None:
        try:
            handle.stop()
        except Exception:
            pass


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


# Definess one instance of the addon data (one per scene)
class FreeSoundData(btypes.PropertyGroup):
    def update_page(self, context):
        if _setting_page or online_access_error():
            return None
        try:
            go_to_page(self, self.current_page)
        except Exception as e:
            print("Freesound Addon --- " + error_message(e))
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

    preview_location: EnumProperty(
        items = [
            ('PROJECT', 'Project Directory', 'Preview will be stored in the project directory'),
            ('COMMON', 'Common Directory', 'Preview will be stored in a common directory specified in preferences'),
        ],
        name="Preview Location",
        default='COMMON',
        description="Where to store downloaded preview sound files"
    )

    download_location: EnumProperty(
        items = [
            ('PROJECT', 'Project Directory', 'Preview will be stored in the Project Directory'),
            ('COMMON', 'Common Directory', 'Preview will be stored in a common directory specified in preferences'),
        ],
        name="Download Location",
        default='PROJECT',
        description="Where to store downloaded sound files"
    )

    current_page: IntProperty(
        description = "Current Pager",
        default=1,
        min=1,
        update=update_page
    )
    pager_num: IntProperty(
        description = "Current pager",
        default = 0
    )
    page_size: IntProperty(
        description = "Number of sounds per result page",
        default = 0
    )
    sounds: IntProperty(
        description = "Number of sounds",
        default = 0
    )
    soundfile: StringProperty(
        name="Sound Path",
        description="Path to the file",
        default=""
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
        return run_page_change(self, context, context.scene.freesound_data.current_page)

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
        api_key = addon_prefs.freesound_api.strip()
        if not api_key or api_key.startswith("Get it here"):
            addon_prefs.freesound_access = False
            self.report({'WARNING'}, 'Insert your Freesound API key first')
            return {'CANCELLED'}
        self.client.set_token(api_key)
        offline = online_access_error()
        if offline:
            self.report({'WARNING'}, offline)
            return {'CANCELLED'}
        try:
            addon_prefs.freesound_access = self.client.check_access()
        except Exception as e:
            self.report({'WARNING'}, 'Unable to reach Freesound. ' + error_message(e))
            return {'CANCELLED'}
        if not addon_prefs.freesound_access:
            self.report({'WARNING'}, 'Invalid Freesound API key')
        return {'FINISHED'}

# Freesound Info
class Freesound_Info(btypes.Operator):
    bl_label = 'Info'
    bl_idname = 'freesound.info'
    bl_description = 'Information about the user and sound'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        item = get_active_item(context.scene.freesound_data)
        if item is None:
            self.report({'WARNING'}, 'Search and select a sound first')
            return {'CANCELLED'}
        url = 'https://freesound.org/people/%s/sounds/%s/' % (quote(item.author), item.sound_id)
        webbrowser.open(url)
        return {'FINISHED'}


# Freesound Add
class Freesound_Add(btypes.Operator):
    bl_label = 'Add'
    bl_idname = 'freesound.add'
    bl_description = 'Add sound to the VSE at current frame'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_data = context.scene.freesound_data

        sound_filepath = get_preview(self, context, addon_data.download_location)
        if sound_filepath is None:
            return {'CANCELLED'}
        sound_name = get_active_item(addon_data).name

        print("Freesound Addon --- Adding Sound Strip : %s" % sound_name)

        # Blender 5.0+ can show a different scene in the sequencer than the active one
        scn = getattr(context, "sequencer_scene", None) or context.scene
        if not scn.sequence_editor:
            scn.sequence_editor_create()
        seq = scn.sequence_editor
        # Blender 4.4 renamed "sequences" to "strips"; the old names were removed in 5.0
        strips = seq.strips if hasattr(seq, "strips") else seq.sequences

        if len(strips) == 0:
            channel = 1
        else:
            channel = min(max(s.channel for s in strips) + 1, MAX_CHANNEL)

        try:
            strips.new_sound(name=sound_name, filepath=sound_filepath,
                             channel=channel, frame_start=scn.frame_current)
        except Exception as e:
            self.report({'WARNING'}, 'Unable to add the sound strip. ' + error_message(e))
            return {'CANCELLED'}
        return {'FINISHED'}

# Freesound Search
class Freesound_Search(btypes.Operator):
    bl_label = 'Search'
    bl_idname = 'freesound.search'
    bl_description = 'Search in Freesound archive'
    bl_options = {'REGISTER', 'UNDO'}
    results_pager = None
    def execute(self, context):
        client = get_client(context)
        addon_data = context.scene.freesound_data

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

        offline = online_access_error()
        if offline:
            self.report({'WARNING'}, offline)
            return {'CANCELLED'}

        rating = addon_data.search_filter
        addon_data.freesound_loading = True
        try:
            pager = client.text_search(query=addon_data.search_item,filter=filter_string, sort=rating,fields="id,name,previews,username,duration,avg_rating,num_ratings,comment,comments")
        except Exception as e:
            self.report({'WARNING'}, 'Search failed. ' + error_message(e))
            return {'CANCELLED'}
        finally:
            addon_data.freesound_loading = False

        Freesound_Search.results_pager = pager
        addon_data.sounds = pager.count
        # Only a full first page tells the real page size
        addon_data.page_size = len(pager.results) if pager.next else max(len(pager.results), 1)
        fill_list(addon_data, pager)
        set_current_page(addon_data, 1)
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
        return run_page_change(self, context, context.scene.freesound_data.current_page + 1)

# Freesound Next 10 pages search
class Freesound_Next10(btypes.Operator):
    bl_label = 'Next 10'
    bl_idname = 'freesound.next10page'
    bl_description = 'Next 10 pages of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return run_page_change(self, context, context.scene.freesound_data.current_page + 10)

# Freesound Last page search
class Freesound_Last(btypes.Operator):
    bl_label = 'Last'
    bl_idname = 'freesound.lastpage'
    bl_description = 'Last page of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return run_page_change(self, context, page_count(context.scene.freesound_data))

# Freesound Prev page search
class Freesound_Prev(btypes.Operator):
    bl_label = 'Prev'
    bl_idname = 'freesound.prevpage'
    bl_description = 'Prev page of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return run_page_change(self, context, context.scene.freesound_data.current_page - 1)

# Freesound Prev 10 pages search
class Freesound_Prev10(btypes.Operator):
    bl_label = 'Prev 10'
    bl_idname = 'freesound.prev10page'
    bl_description = 'Prev 10 pages of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return run_page_change(self, context, context.scene.freesound_data.current_page - 10)

# Freesound First page search
class Freesound_First(btypes.Operator):
    bl_label = 'First'
    bl_idname = 'freesound.firstpage'
    bl_description = 'First page of sounds'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return run_page_change(self, context, 1)

# Freesound Stop
class Freesound_Pause(btypes.Operator):
    bl_label = 'Pause'
    bl_idname = 'freesound.pause'
    bl_description = 'Pause the sound'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        stop_playback()
        context.scene.freesound_data.sound_is_playing = False
        return {'FINISHED'}
