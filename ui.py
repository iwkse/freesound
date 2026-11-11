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
from .freesound import get_active_item, page_count

class FREESOUND_Panel(Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Audio"


class FREESOUND_PT_Panel(FREESOUND_Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Freesound"

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
        addon_prefs =  bpy.context.preferences.addons[__package__].preferences

        layout = self.layout

        if not addon_prefs.freesound_access:
            col = layout.column(align=True)
            col.label(text="No Valid Freesound Credentials", icon="ERROR")
            col.label(text="Check Addon Preferences")            


class FREESOUND_PT_subpanel_search(FREESOUND_Panel):
    bl_parent_id = "FREESOUND_PT_Panel"
    bl_label = "Search"

    @classmethod
    def poll(cls, context):
        return bpy.context.preferences.addons[__package__].preferences.freesound_access

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        addon_data = context.scene.freesound_data
        split = layout.split(factor=0.8, align=True)
        addon_prefs =  bpy.context.preferences.addons[__package__].preferences

        if (addon_prefs.freesound_access == True):

            col = layout.column(align=True)
            split2 = col.row(align=True)
            split2.prop(
                addon_data,
                "search_item",
                text="Search"
            )
            split2.operator("freesound.search", text="", icon='VIEWZOOM')

            col.prop(addon_data, "license", text="License")
            col.prop(addon_data, "search_filter", text="Filter")
            col = col.column(align=True)
            col.prop(addon_data, "duration_from", text="Duration Minimum")
            col.prop(addon_data, "duration_to", text="Maximum")

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

            if addon_data.freesound_list_loaded:
                row.label(text="of %s" % page_count(addon_data))
            else:
                row.label(text="1 of ...")

            row = col_list.row(align=True)
            col = row.column(align=True)
            col.template_list("FREESOUND_UL_List", "", addon_data, "freesound_list", addon_data, "active_list_item")

            col = row.column(align=True)

            if (addon_data.sound_is_playing):
                col.operator("freesound.pause", text="", icon='PAUSE')
            else:
                col.operator("freesound.play", text="", icon='PLAY')
            col.separator()
            col.operator("freesound.add", text="", icon='NLA_PUSHDOWN')
            col.separator()
            col.prop(addon_data, "high_quality", text="", icon="EVENT_H", toggle=True)
            col.separator()
            col.operator("freesound.info", text="", icon='URL')

            item = get_active_item(addon_data)
            if item is None:
                return

            # Ratings go from 0 to 5: draw full and half stars, rounded to the nearest half
            rating = round(item.avg_rating * 2) / 2
            stars = []
            for l in range(5):
                if l + 1 <= rating:
                    stars.append('SOLO_ON')
                elif l + 0.5 == rating:
                    stars.append('SORTBYEXT')
                else:
                    stars.append('SOLO_OFF')

            row = col_list.row(align=True)
            split = row.split(factor=0.4, align=True)
            split.alignment = 'RIGHT'
            split.label(text="Rating (%s)" % item.num_ratings)
            split = split.split(factor=0.2, align=True)
            split.alignment = 'RIGHT'
            for star in stars:
                split.label(text="", icon=star)

            try:
                duration = bpy.utils.smpte_from_seconds(time=float(item.duration))
            except Exception:
                duration = "-"
            row = col_list.row(align=True)
            split = row.split(factor=0.4, align=True)
            split.alignment = 'RIGHT'
            split.label(text="Duration")
            split = split.split(factor=0.6, align=True)
            split.alignment = 'LEFT'
            split.label(text=str(duration))

            row = col_list.row(align=True)
            split = row.split(factor=0.4, align=True)
            split.alignment = 'RIGHT'
            split.label(text="Author")
            split = split.split(factor=0.6, align=True)
            split.alignment = 'LEFT'
            split.label(text=item.author)


class FREESOUND_PT_subpanel_settings(FREESOUND_Panel):
    bl_parent_id = "FREESOUND_PT_Panel"
    bl_label = "Scene Settings"

    def draw(self, context):
        addon_data = context.scene.freesound_data

        layout = self.layout

        box = layout.box()
        box.label(text="Download Locations")

        col = box.column(align=True)
        col.prop(addon_data, "preview_location", text="Preview")
        col.prop(addon_data, "download_location", text="Download")