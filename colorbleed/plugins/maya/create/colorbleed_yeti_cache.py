from collections import OrderedDict

import avalon.maya
from colorbleed.maya import lib


class CreateYetiCache(avalon.maya.Creator):
    """Output for procedural plugin nodes of Yeti """

    name = "yetiDefault"
    label = "Yeti Cache"
    family = "colorbleed.yeticache"
    icon = "pagelines"

    def __init__(self, *args, **kwargs):
        super(CreateYetiCache, self).__init__(*args, **kwargs)

        self.data["peroll"] = 0

        # Add animation data without step and handles
        anim_data = lib.collect_animation_data()
        anim_data.pop("step")
        anim_data.pop("handles")
        self.data.update(anim_data)

        # Add samples
        self.data["samples"] = 3
