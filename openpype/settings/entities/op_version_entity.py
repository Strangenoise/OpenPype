from openpype.lib.openpype_version import (
    op_version_control_available,
    get_remote_versions,
    openpype_path_is_set,
    openpype_path_is_accessible
)
from .input_entities import TextEntity
from .lib import OverrideState


class _OpenPypeVersionInput(TextEntity):
    def _item_initialization(self):
        super(_OpenPypeVersionInput, self)._item_initialization()
        self.multiline = False
        self.placeholder_text = "Latest"
        self.value_hints = []

    def _get_openpype_versions(self):
        return []

    def set_override_state(self, state, *args, **kwargs):
        value_hints = []
        if state is OverrideState.STUDIO:
            versions = self._get_openpype_versions()
            if versions is not None:
                for version in versions:
                    value_hints.append(str(version))

        self.value_hints = value_hints

        super(_OpenPypeVersionInput, self).set_override_state(
            state, *args, **kwargs
        )


class ProductionVersionsInputEntity(_OpenPypeVersionInput):
    schema_types = ["production-versions-text"]

    def _get_openpype_versions(self):
        return ["", "asd", "dsa", "3.6"]
        return get_remote_versions(production=True)


class StagingVersionsInputEntity(_OpenPypeVersionInput):
    schema_types = ["staging-versions-text"]

    def _get_openpype_versions(self):
        return ["", "asd+staging", "dsa+staging", "3.6+staging"]
        return get_remote_versions(staging=True)
