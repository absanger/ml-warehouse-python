import re

from ml_warehouse.ml_warehouse_schema import *
from sqlalchemy import func

ONTTagIdentifierRegex = re.compile(r".*-(\d+)$")

# Sample monkey patches


def _sample_repr(self):
    return "<Sample: name={}, id_sample_lims={} last_updated={}>".format(
        self.name, self.id_sample_lims, self.last_updated
    )


Sample.__repr__ = _sample_repr

Sample.consent_withdrawn.default = False


# Study monkey patches


def _study_repr(self):
    return "<Study: name={}, id_study_lims={} last_updated={}>".format(
        self.name, self.id_study_lims, self.last_updated
    )


Study.__repr__ = _study_repr

Study.last_updated.default = func.now()
Study.recorded_at.default = func.now()
Study.remove_x_and_autosomes.default = False
Study.aligned.default = True
Study.separate_y_chromosome_data.default = False


# OseqFlowcell monkey patches

OseqFlowcell.last_updated.default = func.now()
OseqFlowcell.recorded_at.default = func.now()


@property
def tag_index(self):
    if self.tag_identifier:
        m = ONTTagIdentifierRegex.match(self.tag_identifier)
        if m:
            return int(m.group(1))

    return None


OseqFlowcell.tag_index = tag_index


@property
def tag2_index(self):
    if self.tag2_identifier:
        m = ONTTagIdentifierRegex.match(self.tag2_identifier)
        if m:
            return int(m.group(1))

    return None


OseqFlowcell.tag2_index = tag2_index


def _OseqFlowcell_repr(self):
    return (
        "<OseqFlowcell: inst_name={}, inst_slot={} "
        "expt_name={} tag_set_name={} tag_id={} "
        "last_updated={}>".format(
            self.instrument_name,
            self.instrument_slot,
            self.experiment_name,
            self.tag_set_name,
            self.tag_identifier,
            self.last_updated,
        )
    )


OseqFlowcell.__repr__ = _OseqFlowcell_repr
