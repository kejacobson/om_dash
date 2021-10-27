import pandas as pd
from typing import List

from .recorder_parser import RecorderParser


class RecorderHistoryStacker(RecorderParser):
    def __init__(self, recorder_filenames: List[str]):
        """
        A parser for OpenMDAO recorders that concatenates the histories.
        """
        self.update_histories_from_recorder(recorder_filenames)

    def update_histories_from_recorder(self, recorder_filenames: List[str]):
        start_iteration = 0
        self.objs = self._create_empty_dataframe()
        self.dvs = self._create_empty_dataframe()
        self.cons = self._create_empty_dataframe()
        for i, recorder_file in enumerate(recorder_filenames):
            objs, cons, dvs = self.read_histories_from_recorder(recorder_file, start_iteration)

            # subtract one since the first iteration of the next opt will have the final dvs of the previous
            start_iteration += objs.shape[0] - 1

            if i == 0:
                self.objs = objs
                self.cons = cons
                self.dvs = dvs
            else:
                self.objs = pd.concat([self.objs, objs], axis=0)
                self.cons = pd.concat([self.cons, cons], axis=0)
                self.dvs = pd.concat([self.dvs, dvs], axis=0)
