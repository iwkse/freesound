# Freesound Add-on
Blender Freesound add-on 3.0, for Blender 2.80 and later (tested up to Blender 5.3)

This add-on allows you to browse, listen to and insert sounds from the [freesound.org](https://freesound.org) archive in your Blender VSE.
A free API key is required: you can request it at https://freesound.org/apiv2/apply (a free Freesound account is required).

# What's new in 3.0

- Compatible with Blender 4.4+ and 5.x (new "strips" sequencer API, Python 3.12+, per-workspace sequencer scene).
- HTTPS certificates are verified again, and network calls time out instead of freezing Blender.
- Cached previews are stored per sound and quality (`<id>_<hq|lq>_<name>.mp3`), so sounds with the same name, or HQ and LQ previews, no longer overwrite each other. Previews downloaded with 2.x are downloaded again once.
- Fixed result paging: correct page count, last page reachable, jumping to a typed page number.
- Play, Add and Info always use the selected sound; errors are reported in Blender instead of failing silently.
- Rating shows full and half stars and the number of ratings.

# Installation

**Blender 4.2 and later:** download the latest `freesound-x.y.z.zip` from the [Releases](https://github.com/iwkse/freesound/releases) page and install it with Preferences > Add-ons > Install from Disk. The add-on has also been submitted to the Blender Extensions platform; once approved it will be available in Preferences > Get Extensions.

**Blender 2.80 to 4.1:** clone this repository (or download it as a zip) and install it as a legacy add-on from the Preferences dialog.

Searching and downloading on Blender 4.2 and later require "Allow Online Access" in Preferences > System > Network.

# Usage

Before you start using the add-on you need an API key from Freesound, as described above. Paste it in the add-on preferences and click the Validate button. If everything goes fine the button will say Validated, as in the picture.

![Freesound Setup](https://ibin.co/4Po6Yhu1Se7Y.jpg)

Save the preferences so that the key is not lost.

The add-on panel is in the Video Sequencer: press N to open the sidebar and select the Audio tab.

![Freesound](https://ibin.co/4Po76js8PHnB.jpg)

Using the add-on is straightforward.
Type what you are looking for and click the Search button. More search options are available:
- License filters the results by license.
- Filter sorts the results by relevance, rating or duration.
- Duration Minimum and Maximum search sounds with a specific length: for example, set 2 and 5 to find sounds between 2 and 5 seconds long. -1 means any length.

The page navigation buttons jump to the first page, back 10 pages, forward 10 pages and to the last page; you can also type a page number in the page field.

Select a sound in the list to see its rating, duration and author. The buttons next to the list let you play or pause the preview, add the sound to the sequencer at the current frame, toggle HQ (high quality previews, at the cost of download time and disk space) and open the sound page on freesound.org.

The Scene Settings panel sets where previews and added sounds are stored: in a common folder (set in the add-on preferences) or in a folder next to your .blend file.

Please respect the license of each sound (CC0, CC BY, CC BY-NC...) when using it in your projects.

# Support the project

Freesound add-on is free and open source. If it saves you time, you can support its development:

[Support on Ko-fi](https://ko-fi.com/iwkse)

You can also find this link in the add-on preferences.

# Contributing

If you have any idea, feel free to fork it and submit your changes back to me.

Thanks
