import os
import numpy as np
import pandas as pd
import openmdao.api as om
from openmdao.recorders.sqlite_reader import SqliteCaseReader


class RecorderParser:
    def __init__(self, recorder_filename=''):
        self.read_histories_from_recorder(recorder_filename)

    def read_histories_from_recorder(self, recorder_filename: str):
        self.objs = self._create_empty_dataframe()
        self.dvs = self._create_empty_dataframe()
        self.cons = self._create_empty_dataframe()
        if os.path.exists(recorder_filename):
            case_recorder = om.CaseReader(recorder_filename)
            if len(case_recorder.get_cases()) > 0:
                self.objs, self.dvs = self._parse_objective_and_dv_histories(case_recorder)
                self.cons = self._parse_constraint_history(case_recorder)

    def _create_empty_dataframe(self):
        return pd.DataFrame({'empty': []})

    def _parse_objective_and_dv_histories(self, case_recorder: SqliteCaseReader):
        objs = self._create_empty_dataframe()
        dvs = self._create_empty_dataframe()

        for icase, case in enumerate(case_recorder.get_cases()):
            dv = self._to_dataframe(case.get_design_vars(scaled=False))
            obj = self._to_dataframe(case.get_objectives(scaled=False))

            if icase == 0:
                dvs = dv
                objs = obj
            else:
                dvs = pd.concat([dvs, dv], ignore_index=True)
                objs = pd.concat([objs, obj], ignore_index=True)
        return objs, dvs

    def _parse_constraint_history(self, case_recorder: SqliteCaseReader):
        if self._there_are_no_constraints(case_recorder):
            return self._create_empty_dataframe()

        for icase, case in enumerate(case_recorder.get_cases()):
            con = self._to_dataframe(case.get_constraints(scaled=False))

            if icase == 0:
                cons = con
            else:
                cons = pd.concat([cons, con], ignore_index=True)
        return cons

    def _to_dataframe(self, values_dict: dict):
        new_dict = {}
        for key, vals in values_dict.items():
            if vals.size == 1:
                new_dict[key] = np.array(vals)
            else:
                for i, val in enumerate(vals):
                    new_dict[f'{key}_{i}'] = np.array(val)
        return pd.DataFrame(new_dict)

    def _there_are_no_constraints(self, case_recorder: SqliteCaseReader) -> bool:
        return len(case_recorder.get_case(0).get_constraints().keys()) == 0

    def get_dataframe_of_all_data(self, include_constraints=True, include_dvs=True) -> pd.DataFrame:
        if self._no_data_has_been_read():
            return self._create_empty_dataframe()

        data = [self.objs]
        if self.cons.size > 0 and include_constraints:
            data.append(self.cons)
        if self.dvs.size > 0 and include_dvs:
            data.append(self.dvs)
        return pd.concat(data, axis=1)

    def get_dataframe_of_objectives_and_constraints(self) -> pd.DataFrame:
        if self._no_data_has_been_read():
            return self._create_empty_dataframe()

        if self.cons.size > 0:
            return pd.concat([self.objs, self.cons], axis=1)
        else:
            return self.objs

    def _no_data_has_been_read(self):
        return self.objs.size == 0

    def write_data_to_tecplot(self, tecplot_filename):
        all_data = self.get_dataframe_of_all_data()
        vars = 'Iteration'
        for var in all_data.keys():
            vars += f' "{var}"'
        header = (f'TITLE     = "OpenMDAO Record"\n'
                  + f'VARIABLES ={vars}\n'
                  + f'ZONE T="OpenMDAO"  I={all_data.shape[0]}, ZONETYPE=Ordered DATAPACKING=POINT')
        np.savetxt(tecplot_filename, all_data.to_records(), header=header, comments='')
