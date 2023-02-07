import os
import copy

from maya import cmds
import arnold

from openpype.pipeline import publish
from openpype.hosts.maya.api.lib import maintained_selection, attribute_values
from openpype.lib import StringTemplate


class ExtractArnoldSceneSource(publish.Extractor):
    """Extract the content of the instance to an Arnold Scene Source file."""

    label = "Arnold Scene Source"
    hosts = ["maya"]
    families = ["ass"]
    asciiAss = False

    def process(self, instance):
        staging_dir = self.staging_dir(instance)
        filename = "{}.ass".format(instance.name)
        file_path = os.path.join(staging_dir, filename)

        # Mask
        mask = arnold.AI_NODE_ALL

        node_types = {
            "options": arnold.AI_NODE_OPTIONS,
            "camera": arnold.AI_NODE_CAMERA,
            "light": arnold.AI_NODE_LIGHT,
            "shape": arnold.AI_NODE_SHAPE,
            "shader": arnold.AI_NODE_SHADER,
            "override": arnold.AI_NODE_OVERRIDE,
            "driver": arnold.AI_NODE_DRIVER,
            "filter": arnold.AI_NODE_FILTER,
            "color_manager": arnold.AI_NODE_COLOR_MANAGER,
            "operator": arnold.AI_NODE_OPERATOR
        }

        for key in node_types.keys():
            if instance.data.get("mask" + key.title()):
                mask = mask ^ node_types[key]

        # Motion blur
        attribute_data = {
            "defaultArnoldRenderOptions.motion_blur_enable": instance.data.get(
                "motionBlur", True
            ),
            "defaultArnoldRenderOptions.motion_steps": instance.data.get(
                "motionBlurKeys", 2
            ),
            "defaultArnoldRenderOptions.motion_frames": instance.data.get(
                "motionBlurLength", 0.5
            )
        }

        # Write out .ass file
        kwargs = {
            "filename": file_path,
            "startFrame": instance.data.get("frameStartHandle", 1),
            "endFrame": instance.data.get("frameEndHandle", 1),
            "frameStep": instance.data.get("step", 1),
            "selected": True,
            "asciiAss": self.asciiAss,
            "shadowLinks": True,
            "lightLinks": True,
            "boundingBox": True,
            "expandProcedurals": instance.data.get("expandProcedurals", False),
            "camera": instance.data["camera"],
            "mask": mask
        }

        filenames = self._extract(
            instance.data["setMembers"], attribute_data, kwargs
        )

        if "representations" not in instance.data:
            instance.data["representations"] = []

        representation = {
            "name": "ass",
            "ext": "ass",
            "files": filenames if len(filenames) > 1 else filenames[0],
            "stagingDir": staging_dir,
            "frameStart": kwargs["startFrame"]
        }

        instance.data["representations"].append(representation)

        self.log.info(
            "Extracted instance {} to: {}".format(instance.name, staging_dir)
        )

        # Extract proxy.
        kwargs["filename"] = file_path.replace(".ass", "_proxy.ass")
        filenames = self._extract(
            instance.data["proxy"], attribute_data, kwargs
        )

        template_data = copy.deepcopy(instance.data["anatomyData"])
        template_data.update({"ext": "ass"})
        templates = instance.context.data["anatomy"].templates["publish"]
        published_filename_without_extension = StringTemplate(
            templates["file"]
        ).format(template_data).replace(".ass", "_proxy")
        transfers = []
        for filename in filenames:
            source = os.path.join(staging_dir, filename)
            destination = os.path.join(
                instance.data["resourcesDir"],
                filename.replace(
                    filename.split(".")[0],
                    published_filename_without_extension
                )
            )
            transfers.append((source, destination))

        for source, destination in transfers:
            self.log.debug("Transfer: {} > {}".format(source, destination))

        instance.data["transfers"] = transfers

    def _extract(self, nodes, attribute_data, kwargs):
        self.log.info("Writing: " + kwargs["filename"])
        filenames = []
        with attribute_values(attribute_data):
            with maintained_selection():
                self.log.info(
                    "Writing: {}".format(nodes)
                )
                cmds.select(nodes, noExpand=True)

                self.log.info(
                    "Extracting ass sequence with: {}".format(kwargs)
                )

                exported_files = cmds.arnoldExportAss(**kwargs)

                for file in exported_files:
                    filenames.append(os.path.split(file)[1])

                self.log.info("Exported: {}".format(filenames))

        return filenames
