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
import freesound
from . import freesound_data 

class SEQUENCER_EXTRA_MT_input(bpy.types.Menu):
    bl_label = "Input"

    def draw(self, context):
        self.layout.operator_context = 'INVOKE_REGION_WIN'
        self.layout.operator('sequencerextra.striprename',
        text='File Name to Strip Name', icon='PLUGIN')
        self.layout.operator('sequencerextra.editexternally',
        text='Open with External Editor', icon='PLUGIN')
        self.layout.operator('sequencerextra.edit',
        text='Open with Editor', icon='PLUGIN')
        self.layout.operator('sequencerextra.createmovieclip',
        text='Create Movieclip strip', icon='PLUGIN')


def sequencer_add_menu_func(self, context):
    self.layout.operator('sequencerextra.recursiveload', 
    text='recursive load from browser', icon='PLUGIN')
    self.layout.separator()


def sequencer_select_menu_func(self, context):
    self.layout.operator_menu_enum('sequencerextra.select_all_by_type',
    'type', text='All by Type', icon='PLUGIN')
    self.layout.separator()
    self.layout.operator('sequencerextra.selectcurrentframe',
    text='Before Current Frame', icon='PLUGIN').mode = 'BEFORE'
    self.layout.operator('sequencerextra.selectcurrentframe',
    text='After Current Frame', icon='PLUGIN').mode = 'AFTER'
    self.layout.operator('sequencerextra.selectcurrentframe',
    text='On Current Frame', icon='PLUGIN').mode = 'ON'
    self.layout.separator()
    self.layout.operator('sequencerextra.selectsamechannel',
    text='Same Channel', icon='PLUGIN')


def sequencer_strip_menu_func(self, context):
    self.layout.operator('sequencerextra.extendtofill',
    text='Extend to Fill', icon='PLUGIN')
    self.layout.operator('sequencerextra.distribute',
    text='Distribute', icon='PLUGIN')
    self.layout.operator_menu_enum('sequencerextra.fadeinout',
    'mode', text='Fade', icon='PLUGIN')
    self.layout.operator_menu_enum('sequencerextra.copyproperties',
    'prop', icon='PLUGIN')
    self.layout.operator('sequencerextra.slidegrab',
    text='Slide Grab', icon='PLUGIN')
    self.layout.operator_menu_enum('sequencerextra.slide',
    'mode', icon='PLUGIN')
    self.layout.operator('sequencerextra.insert',
    text='Insert (Single Channel)', icon='PLUGIN').singlechannel = True
    self.layout.operator('sequencerextra.insert',
    text='Insert', icon='PLUGIN').singlechannel = False
    self.layout.operator('sequencerextra.ripplecut',
    text='Ripple Cut', icon='PLUGIN')
    self.layout.operator('sequencerextra.rippledelete',
    text='Ripple Delete', icon='PLUGIN')
    self.layout.separator()


def sequencer_header_func(self, context):
    self.layout.menu("SEQUENCER_EXTRA_MT_input")
    if context.space_data.view_type in ('PREVIEW', 'SEQUENCER_PREVIEW'):
        self.layout.operator('sequencerextra.jogshuttle',
        text='Jog/Shuttle', icon='NDOF_TURN')
    if context.space_data.view_type in ('SEQUENCER', 'SEQUENCER_PREVIEW'):
        self.layout.operator('sequencerextra.navigateup',
        text='Navigate Up', icon='FILE_PARENT')
    if context.space_data.view_type in ('SEQUENCER', 'SEQUENCER_PREVIEW'):
        self.layout.operator('sequencerextra.placefromfilebrowser',
        text='File Place', icon='TRIA_DOWN').insert = False
    if context.space_data.view_type in ('SEQUENCER', 'SEQUENCER_PREVIEW'):
        self.layout.operator('sequencerextra.placefromfilebrowser',
        text='File Insert', icon='TRIA_RIGHT').insert = True
    if context.space_data.view_type in ('SEQUENCER', 'SEQUENCER_PREVIEW'):
        self.layout.operator('sequencerextra.placefromfilebrowserproxy',
        text='Proxy Place', icon='TRIA_DOWN')
    if context.space_data.view_type in ('SEQUENCER', 'SEQUENCER_PREVIEW'):
        self.layout.operator('sequencerextra.placefromfilebrowserproxy',
        text='Proxy Insert', icon='TRIA_RIGHT').insert = True


def time_frame_menu_func(self, context):
    self.layout.operator('timeextra.trimtimelinetoselection',
    text='Trim to Selection', icon='PLUGIN')
    self.layout.operator('timeextra.trimtimeline',
    text='Trim to Timeline Content', icon='PLUGIN')
    self.layout.separator()
    self.layout.operator('screenextra.frame_skip',
    text='Skip Forward One Second', icon='PLUGIN').back = False
    self.layout.operator('screenextra.frame_skip',
    text='Skip Back One Second', icon='PLUGIN').back = True
    self.layout.separator()


def time_header_func(self, context):
    self.layout.operator('sequencerextra.jogshuttle',
    text='Jog/Shuttle', icon='NDOF_TURN')


def clip_header_func(self, context):
    self.layout.operator('sequencerextra.jogshuttle',
    text='Jog/Shuttle', icon='NDOF_TURN')


def clip_clip_menu_func(self, context):
    self.layout.operator('clipextra.openactivestrip',
    text='Open Active Strip', icon='PLUGIN')
    self.layout.operator('clipextra.openfromfilebrowser',
    text='Open from File Browser', icon='PLUGIN')
    self.layout.separator()

class FreesoundPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Freesound"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    @staticmethod
    def has_sequencer(context):
        return (context.space_data.view_type\
        in {'SEQUENCER', 'SEQUENCER_PREVIEW'})

    @classmethod
    def poll(cls, context):
        return cls.has_sequencer(context)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="")

    def draw(self, context):
        layout = self.layout
        sce = context.scene

        frame_current = sce.frame_current
        freesound_api = context.scene.freesound_data.freesound_api
        addon_data = context.scene.freesound_data
        split = layout.split(percentage=0.8)


        if (addon_data.freesound_access):
            split.prop(
                addon_data,
                "freesound_api",
                text="Api Key")
            split.operator("freesound.connect", text='Connect', icon='PLUGIN')
            split2 = layout.split(percentage=0.8)
            split2.prop(
                addon_data,
                "search_item",
                text=""
            )
            split2.operator("freesound.search", text="Search", icon='VIEWZOOM')
            freesound_ptr = bpy.types.AnyType(bpy.context.scene.freesound_data)
            split3 = layout.split(percentage=0.9)
            split3.template_list("FREESOUNDList", "", freesound_ptr, "freesound_list", freesound_ptr, "active_list_item", type='DEFAULT')
            col = split3.column(align=True)
            col.operator("freesound.play", icon='TRIA_RIGHT')
            col.operator("freesound.add", icon='ZOOMIN')
            col.operator("freesound.nextpage", icon='PLAY_AUDIO')

        else:
            split.prop(
                addon_data,
                "freesound_api",
                text="Api Key")
            split.operator("freesound.connect", text='Connect', icon='PLUGIN')
