import os
from typing import List
import numpy as np


class BgsResidualParser:
    def __init__(self):
        self.all_data: List[np.ndarray] = []

    def parse_residuals(self, filename: str, doing_nlbgs: bool):
        lines = self._grep_for_lines_with_bgs_residuals(filename, doing_nlbgs)
        self.all_data = self._get_residual_data_from_lines(lines, doing_nlbgs)

    def _grep_for_lines_with_bgs_residuals(self, filename: str, doing_nlbgs: bool):
        prefix = 'NL: NLBGS' if doing_nlbgs else 'LN: LNBGS'
        return os.popen(f'grep -E "{prefix} [0-9]" {filename}').read().split('\n')[:-1]

    def _split_line_into_residual_data(self, line: str, nlbgs: bool):
        key = 'NLBGS' if nlbgs else 'LNBGS'
        iteration = int(line.split(';')[0].split(key)[-1])
        abs_resid = float(line.split(';')[-1].split(' ')[1])
        rel_resid = float(line.split(';')[-1].split(' ')[2])
        return iteration, abs_resid, rel_resid

    def _get_residual_data_from_lines(self, lines: List[str],
                                      doing_nlbgs: bool) -> List[np.ndarray]:
        all_data = []
        current_solve = []
        start_iteration = 1 if doing_nlbgs else 0
        for line in lines:
            iteration, abs_resid, rel_resid = self._split_line_into_residual_data(line, doing_nlbgs)
            if iteration == start_iteration and self._is_not_first_line(current_solve):
                all_data.append(np.array(current_solve))
                current_solve = []
            current_solve.append([iteration, abs_resid, rel_resid])

        # append the last solve
        all_data.append(np.array(current_solve))
        return all_data

    def _is_not_first_line(self, current_solve):
        return len(current_solve) > 0
