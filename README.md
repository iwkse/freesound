# Freesound Add-on
Blender Freesound add-on 3.0, for Blender 2.80 and later (tested up to Blender 5.3)

This add-on allows you to browse, listen and insert sounds from the freesound.org archive in your Blender VSE.
An API key is required: you can request it from https://freesound.org/apiv2/apply (Freesound login is required)
The plugin documentation button opens the API freesound page as well.

# What's new in 3.0

- Compatible with Blender 4.4+ and 5.x (new "strips" sequencer API, Python 3.12+, per-workspace sequencer scene).
- HTTPS certificates are verified again, and network calls time out instead of freezing Blender.
- Cached previews are stored per sound and quality (`<id>_<hq|lq>_<name>.mp3`), so sounds with the same name, or HQ and LQ previews, no longer overwrite each other. Previews downloaded with 2.x are downloaded again once.
- Fixed result paging: correct page count, last page reachable, jumping to a typed page number.
- Play, Add and Info always use the selected sound; errors are reported in Blender instead of failing silently.
- Rating shows full and half stars and the number of ratings.

# Installation
**Blender 4.2 and later:** install it as an extension, from the Blender Extensions platform (Preferences > Get Extensions, search "Freesound") or from the release zip with Preferences > Add-ons > Install from Disk. Searching and downloading require "Allow Online Access" in Preferences > System > Network.

**Blender 2.80 to 4.1:** clone the GIT repository or download the release and manually install it from the user preferences dialog as a legacy add-on.

To build the extension package yourself:

    blender --command extension build --source-dir . --output-dir dist

# Usage

Before to start using the add-on you need to get an API key from freesound as decribed above. After this you insert the API and click on Validate button. If everything go fine you will see the button saying Validated as in the picture.

![Freesound Setup](https://ibin.co/4Po6Yhu1Se7Y.jpg)

Now you can save preferences so that the value is not lost.

![Freesound](https://ibin.co/4Po76js8PHnB.jpg)

Using the add-on is straightforward and intuitive.
All you have to do is search for some sounds and click on the Search button. You got further options for searching, HQ (High Quality Preview) allows you to download the best available preview at cost of download speed and disk space. 
The "from" "to" range allows you to search sounds with a specific length. You can for example search a sound which is at least 2 seconds and max 5 seconds if you set 2 and 5 in the fields.
The next box allows you to sort sounds based on rating.
Last box allows you to filter by license.

The page navigation buttons allow you respectively to jump to the first and last page, increment by 10 or 1 or add an arbitrary number in the page field.

# Contributing

If you have any idea, feel free to fork it and submit your changes back to me.

Thanks
