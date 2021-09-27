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
import datetime

class FREESOUND_PT_Panel(Panel):
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
        layout.use_property_split = True
        layout.use_property_decorate = False
        sce = context.scene

        frame_current = sce.frame_current
        addon_data = context.scene.freesound_data
        split = layout.split(factor=0.8, align=True)
        addon_prefs =  bpy.context.preferences.addons[__package__].preferences


        if (addon_prefs.freesound_access == True):

            col = layout.column(align=True)

            col.prop(addon_data, "license", text="License")
            col.prop(addon_data, "search_filter", text="Filter")
            col = col.column(align=True)
            col.prop(addon_data, "duration_from", text="Duration Minimum")
            col.prop(addon_data, "duration_to", text="Maximum")

            split2 = col.row(align=True)
            split2.prop(
                addon_data,
                "search_item",
                text="Search"
            )
            split2.operator("freesound.search", text="", icon='VIEWZOOM')

            col = layout.box()
            col_list = col.column(align=True)
            row = col_list.row(align=True)
            row.alignment = 'CENTER'
            row.label(text="List Page")
            row.operator("freesound.firstpage", icon='REW', text="")
            row.operator("freesound.prev10page", icon='TRIA_LEFT', text="")
            row.prop(addon_data, "current_page", text="")
            row.operator("freesound.next10page", icon='TRIA_RIGHT', text="")
            row.operator("freesound.lastpage", icon='FF', text="")

            try:
                pages = int(addon_data.sounds/len(addon_data.freesound_list))
                row.label(text="of %s" % str(pages))
            except:
                row.label(text="1 of ...")

            freesound_ptr = bpy.types.AnyType(bpy.context.scene.freesound_data)

            row = col_list.row(align=True)
            col = row.column(align=True)
            col.template_list("FREESOUND_UL_List", "", freesound_ptr, "freesound_list", freesound_ptr, "active_list_item")

            col = row.column(align=True)

            if (addon_data.sound_is_playing):
                col.operator("freesound.pause", text="", icon='PAUSE')
            else:
                col.operator("freesound.play", text="", icon='PLAY')
            col.separator()
            col.operator("freesound.info", text="", icon='URL')
            col.separator()
            col.operator("freesound.add", text="", icon='NLA_PUSHDOWN')

            col_list.prop(addon_data, "high_quality", text="Use High Quality File")

            row = col_list.row(align=True)
            row.alignment = 'RIGHT'
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
                        val[l] = 'SOLO_OFF'
                elif ((point_star % 1) <= 0.5 and (point_star % 1) != 0):
                        val[l] = 'SORTBYEXT'
                elif ((point_star % 1) == 0):
                        val[l] = 'SOLO_OFF'

            if (addon_data.freesound_list_loaded):
                try:
                    num_ratings = addon_data.freesound_list[addon_data.active_list_item].num_ratings
                except:
                    num_ratings = 0
                row.label(text="Rating ")
                row.label(text="", icon=val[0])
                row.label(text="", icon=val[1])
                row.label(text="", icon=val[2])
                row.label(text="", icon=val[3])
                row.label(text="", icon=val[4])

            row = col_list.row()
            row.alignment = 'RIGHT'
            try:
                duration = addon_data.freesound_list[addon_data.active_list_item].duration
            except:
                duration = 0
            row.label(text="Duration  " + str(bpy.utils.smpte_from_seconds(time=float(duration))))

            row = col_list.row()
            row.alignment = 'RIGHT'

            try:
                author = addon_data.freesound_list[addon_data.active_list_item].author
            except:
                author = "Unknown"
            row.label(text="Author  " + author)
