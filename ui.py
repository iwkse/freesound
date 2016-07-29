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
from . import freesound_api
from . import freesound

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
        addon_data = context.scene.freesound_data
        split = layout.split(percentage=0.8)
        addon_prefs =  bpy.context.user_preferences.addons[__package__].preferences


        if (addon_prefs.freesound_access == True):

            split2 = layout.split(percentage=0.8)
            split2.prop(
                addon_data,
                "search_item",
                text=""
            )
            split2.operator("freesound.search", text="Search", icon='VIEWZOOM')
            row = layout.row()
            split3 = layout.split(percentage=0.1)
            split3.prop(addon_data, "high_quality")
            split3.prop(addon_data, "duration_from", "from")
            split3.prop(addon_data, "duration_to", "to")
            split3.prop(addon_data, "license")
            freesound_ptr = bpy.types.AnyType(bpy.context.scene.freesound_data)
            split3 = layout.split(percentage=1)
            split3.template_list("FREESOUNDList", "", freesound_ptr, "freesound_list", freesound_ptr, "active_list_item", type='DEFAULT')
            col = split3.column(align=True)
       #     if (addon_data.sound_is_playing):
       #         col.operator("freesound.pause", icon='PAUSE')
       #     else:
       #         col.operator("freesound.play", icon='PLAY')

       #     col.operator("freesound.add", icon='ZOOMIN')
            row = layout.row()

            row.operator("freesound.prevpage", icon='REW', text="")
            row.operator("freesound.prevpage", icon='PREV_KEYFRAME', text="")
            row.operator("freesound.prevpage", icon='PLAY_REVERSE', text="")
            row.prop(addon_data, "duration_from", "pages")
            row.operator("freesound.nextpage", icon='PLAY', text="")
            row.operator("freesound.prevpage", icon='NEXT_KEYFRAME', text="")
            row.operator("freesound.prevpage", icon='FF', text="")
