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
from bpy.types import Panel
from . import freesound_api
from . import freesound

class Freesound_Panel(Panel):
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
        split = layout.split(factor=0.8, align=True)
        addon_prefs =  bpy.context.user_preferences.addons[__package__].preferences


        if (addon_prefs.freesound_access == True):

            split2 = layout.split(factor=0.8, align=True)
            split2.prop(
                addon_data,
                "search_item",
                text=""
            )
            split2.operator("freesound.search", text="Search", icon='VIEWZOOM')

            split3 = layout.split(factor=0.1, align=True)
            split3.prop(addon_data, "high_quality")
            split3.prop(addon_data, "duration_from", text="from")
            split3.prop(addon_data, "duration_to", text="to")
            split3.prop(addon_data, "search_filter")
            split3.prop(addon_data, "license")
            freesound_ptr = bpy.types.AnyType(bpy.context.scene.freesound_data)
            
            row = layout.row()
            col = row.column(align=True)

            if (addon_data.sound_is_playing):
                col.operator("freesound.pause", text="", icon='MUTE_IPO_OFF')
            else:
                col.operator("freesound.play", text="", icon='MUTE_IPO_ON') 

            col.operator("freesound.add", text="", icon='PLUS')
            col.operator("freesound.info", text="", icon='INFO')
            col = row.column(align=True)


            col.template_list("FREESOUNDList", "", freesound_ptr, "freesound_list", freesound_ptr, "active_list_item")
            
            row = layout.row()

            row.operator("freesound.firstpage", icon='REW', text="")
            row.operator("freesound.prev10page", icon='PREV_KEYFRAME', text="")
            row.operator("freesound.prevpage", icon='PLAY_REVERSE', text="")
            split = row.split(factor=0.5, align=True)
            
            split.prop(addon_data, "current_page", text="Page")

            try:
                pages = int(addon_data.sounds/len(addon_data.freesound_list))
                split.label(text="of     %s " % str(pages))
            except:
                split.label(text="1 of ...")
            
            val = [0,1,2,3,4]
            point_star = 0
            try:
                point_star = addon_data.freesound_list[addon_data.active_list_item].avg_rating
            except:
                point_star = 0
            for l in val:
                if (l <= point_star-1):
                    val[l] = 'SOLO_ON'
                elif ((point_star % 1) > 0.5):
                        val[l] = 'NONE'
                elif ((point_star % 1) <= 0.5 and (point_star % 1) != 0):
                        val[l] = 'MARKER_HLT'
                elif ((point_star % 1) == 0):
                        val[l] = 'SOLO_OFF'
            
            if (addon_data.freesound_list_loaded):
                split = split.split(factor=0.1, align=True)
                split.label(text="",  icon=val[0])
                split = split.split(factor=0.1, align=True)
                split.label(text="", icon=val[1])
                split = split.split(factor=0.1, align=True)
                split.label(text="", icon=val[2])
                split = split.split(factor=0.1, align=True)
                split.label(text="", icon=val[3])
                split = split.split(factor=0.1, align=True)
                split.label(text="", icon=val[4])
            
            row.operator("freesound.nextpage", icon='PLAY', text="")
            row.operator("freesound.next10page", icon='NEXT_KEYFRAME', text="")
            row.operator("freesound.lastpage", icon='FF', text="")

