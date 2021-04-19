from ortools.sat.python import cp_model
import numpy as np
import pandas as pd


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.solutions_ = 0
        # self.arr_ = arr
        # self.grid_size = grid_size

    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        print("solution", self.solutions_)

        # for i in range(self.grid_size):
        #     for j in range(self.grid_size):
        #         self.Solve


data = {'puzzle': ["000000030705020000090000400000004002059600008300010050570060100000300000600400005"],
        'solution': [0]}
sudoku = pd.DataFrame(data=data)
sample = sudoku.loc[0]  # row 2020


## Transform an encoded puzzle into an integer matrix
def string_conversion_into_matrix(sample: str):
    return np.matrix([np.array(list(sample[i:i + 9])).astype(int) for i in range(0, len(sample), 9)])


## Transform an integer matrix into an encoded string
def sudoku_array_into_string(sudoku: np.matrix):
    return ''.join([''.join(list(r.astype(str))) for r in np.asarray(sudoku)])


sudoku_array = string_conversion_into_matrix(sample['puzzle'])
sudoku_string = sudoku_array_into_string(sudoku_array)
assert sudoku_string == sample['puzzle']  # must be true, since the same puzzle was decoded and encoded


def solve_with_cp(sudoku_grid: np.matrix):
    # Sudoku instance (np.matrix) with CP modeling. Returns a tuple with the resulting matrix and the
    # execution time in seconds.
    assert sudoku_grid.shape == (9, 9)

    sudoku_grid_size = 9
    region_size = 3
    model = cp_model.CpModel()  # Step 1

    # Step2: Create and initialize variables.
    x = {}
    for i in range(sudoku_grid_size):
        for j in range(sudoku_grid_size):
            if sudoku_grid[i, j] != 0:
                x[i, j] = sudoku_grid[i, j]  # Initial values (values already defined on the puzzle).
            else:
                x[i, j] = model.NewIntVar(1, sudoku_grid_size,
                                          'x[{},{}]'.format(i, j))  # Values to be found (variyng from 1 to 9).

    # Step3: Values constraints.
    # AllDifferent on rows, to declare that all elements of all rows must be different.
    for i in range(sudoku_grid_size):
        model.AddAllDifferent([x[i, j] for j in range(sudoku_grid_size)])

    # AllDifferent on columns, to declare that all elements of all columns must be different.
    for j in range(sudoku_grid_size):
        model.AddAllDifferent([x[i, j] for i in range(sudoku_grid_size)])

    # AllDifferent on regions, to declare that all elements of all regions must be different.
    for row_idx in range(0, sudoku_grid_size, region_size):
        for col_idx in range(0, sudoku_grid_size, region_size):
            model.AddAllDifferent(
                [x[row_idx + i, j] for j in range(col_idx, (col_idx + region_size)) for i in range(region_size)])

    # Step 4
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    result = np.zeros((sudoku_grid_size, sudoku_grid_size)).astype(int)

    # Step 6: Getting values defined by the solver
    if status == (cp_model.OPTIMAL or cp_model.FEASIBLE):
        for i in range(sudoku_grid_size):
            for j in range(sudoku_grid_size):
                result[i, j] = int(solver.Value(x[i, j]))
    else:
        raise Exception('Unfeasible Sudoku')

    solver.SearchForAllSolutions(model, SolutionPrinter())
    return result


res = solve_with_cp(sudoku_array)
cp_solution = sudoku_array_into_string(res)
print(sample["puzzle"])
print(cp_solution)
