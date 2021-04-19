########################################################################################
print("################################################################################")
print("################################################################################")
print("#########################       Task : 1       #################################")
print("################################################################################")
print("################################################################################")
########################################################################################
from ortools.sat.python import cp_model

# Extract information from sentences and stored in list
students = ["Carol", "Elisa", "Oliver", "Lucas"]
university_names = ["London", "Cambridge", "Oxford", "Edinburgh"]
nationalities = ["Australia", "USA", "Canada", "South Africa"]
courses = ["History", "Medicine", "Law", "Architecture"]
students_gender = ["Boy", "Girl"]


# SolutionPrinter class is used for retrieving all solution
class SolutionPrinter_1(cp_model.CpSolverSolutionCallback):
    def __init__(self, university_name, nationality, course, student_gender):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.nationality = nationality
        self.university_name = university_name
        self.course = course
        self.student_gender = student_gender
        self.solutions_ = 0

    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        print("solution", self.solutions_)

        for student in students:
            print(" - " + student + ":")
            for university_name in university_names:
                if self.Value(self.university_name[student][university_name]):
                    print("    - ", university_name)
            for nationality in nationalities:
                if self.Value(self.nationality[student][nationality]):
                    print("    - ", nationality)
            for course in courses:
                if self.Value(self.course[student][course]):
                    print("    - ", course)
            for gender in students_gender:
                if self.Value(self.student_gender[student][gender]):
                    print("    - ", gender)


# Task 1 :
def task_1():
    # Initialize CP_model:
    model = cp_model.CpModel()

    # Define Variables
    # a. University
    # b. Nationality
    # c. Gender
    # d. Course
    student_university_name = {}
    for student in students:
        variables = {}
        for university_name in university_names:
            variables[university_name] = model.NewBoolVar(student + university_name)
        student_university_name[student] = variables

    student_nationality = {}
    for student in students:
        variables = {}
        for nationality in nationalities:
            variables[nationality] = model.NewBoolVar(student + nationality)
        student_nationality[student] = variables

    student_course = {}
    for student in students:
        variables = {}
        for course in courses:
            variables[course] = model.NewBoolVar(student + course)
        student_course[student] = variables

    student_student_gender = {}
    for student in students:
        variables = {}
        for student_gender in students_gender:
            variables[student_gender] = model.NewBoolVar(student + student_gender)
        student_student_gender[student] = variables

    # Define constraints -
    for i in range(len(students)):
        # sentence 1 - One of them is going to London (1).
        for j in range(i + 1, len(students)):
            model.AddBoolAnd([student_university_name[students[j]]["London"].Not()]).OnlyEnforceIf(
                student_university_name[students[i]]["London"])

        # sentence 6 -The student from Canada is a historian or will go to Oxford (6).
        model.AddBoolOr([student_university_name[students[i]]["Oxford"],
                         student_course[students[i]]["History"]]).OnlyEnforceIf(
            student_nationality[students[i]]["Canada"])

        # Sentence 7 - The student from South Africa is going to Edinburgh or will study Law (7).
        model.AddBoolOr([student_university_name[students[i]]["Edinburgh"],
                         student_course[students[i]]["Law"]]).OnlyEnforceIf(
            student_nationality[students[i]]["South Africa"])

    # Sentence 2 - Exactly one boy and one girl chose a university in a city with the same initial of their names (2).
    model.AddBoolOr([
        student_university_name["Oliver"]["Oxford"],
        student_university_name["Lucas"]["London"]])

    model.AddBoolOr([
        student_university_name["Oliver"]["Oxford"].Not(),
        student_university_name["Lucas"]["London"].Not()])

    model.AddBoolOr([
        student_university_name["Carol"]["Cambridge"],
        student_university_name["Elisa"]["Edinburgh"]])

    model.AddBoolOr([
        student_university_name["Carol"]["Cambridge"].Not(),
        student_university_name["Elisa"]["Edinburgh"].Not()])

    model.AddBoolOr([
        student_university_name["Carol"]["Cambridge"]]).OnlyEnforceIf(
        student_university_name["Elisa"]["Edinburgh"].Not())

    model.AddBoolOr([
        student_university_name["Elisa"]["Edinburgh"]]).OnlyEnforceIf(
        student_university_name["Carol"]["Cambridge"].Not())

    model.AddBoolOr([
        student_university_name["Oliver"]["Oxford"]]).OnlyEnforceIf(student_university_name["Lucas"]["London"].Not())

    model.AddBoolOr([
        student_university_name["Lucas"]["London"]]).OnlyEnforceIf(student_university_name["Oliver"]["Oxford"].Not())

    # Sentence 3 - A boy is from Australia, the other studies History (3).
    model.AddBoolOr([
        student_nationality["Oliver"]["Australia"],
        student_nationality["Lucas"]["Australia"]])
    model.AddBoolOr([
        student_course["Oliver"]["History"]]).OnlyEnforceIf(student_nationality["Lucas"]["Australia"])
    model.AddBoolOr([
        student_course["Lucas"]["History"]]).OnlyEnforceIf(student_nationality["Oliver"]["Australia"])
    model.AddBoolAnd([
        student_nationality["Carol"]["Australia"].Not(),
        student_nationality["Elisa"]["Australia"].Not(),
        student_course["Carol"]["History"].Not(),
        student_course["Elisa"]["History"].Not()])

    # Sentence 4. A girl goes to Cambridge, the other studies Medicine (4).
    model.AddBoolOr([
        student_university_name["Carol"]["Cambridge"],
        student_university_name["Elisa"]["Cambridge"]])

    model.AddBoolOr([
        student_course["Elisa"]["Medicine"]]).OnlyEnforceIf(student_university_name["Carol"]["Cambridge"])

    model.AddBoolOr([
        student_course["Carol"]["Medicine"]]).OnlyEnforceIf(student_university_name["Elisa"]["Cambridge"])

    model.AddBoolAnd([
        student_university_name["Oliver"]["Cambridge"].Not(),
        student_university_name["Lucas"]["Cambridge"].Not(),
        student_course["Oliver"]["Medicine"].Not(),
        student_course["Lucas"]["Medicine"].Not()])

    # Sentence 5 - Oliver studies Law or is from USA; He is not from South Africa (5).
    # model.AddBoolOr([
    #     student_nationality["Oliver"]["USA"],
    #     student_course["Oliver"]["Law"]])

    model.AddBoolOr([student_nationality["Oliver"]["South Africa"].Not()])

    model.AddBoolAnd([
        student_nationality["Oliver"]["USA"],
        student_nationality["Oliver"]["South Africa"].Not()]).OnlyEnforceIf(student_course["Oliver"]["Law"].Not())

    model.AddBoolAnd([
        student_course["Oliver"]["Law"],
        student_nationality["Oliver"]["South Africa"].Not()]).OnlyEnforceIf(student_nationality["Oliver"]["USA"].Not())

    # IMPLICIT CONSTRAINTS

    # Every student has one nationality
    for student in students:
        variables = []
        for countryName in nationalities:
            variables.append(student_nationality[student][countryName])
        model.AddBoolOr(variables)

    # Every student has one university
    for student in students:
        variables = []
        for universityName in university_names:
            variables.append(student_university_name[student][universityName])
        model.AddBoolOr(variables)

    # Every student has one course
    for student in students:
        variables = []
        for courseName in courses:
            variables.append(student_course[student][courseName])
        model.AddBoolOr(variables)

    for i in range(4):
        for j in range(i + 1, 4):
            for k in range(4):
                # Every student has  different/unique country
                model.AddBoolOr([
                    student_nationality[students[i]][nationalities[k]].Not(),
                    student_nationality[students[j]][nationalities[k]].Not()])
                # Every student has a different/unique university
                model.AddBoolOr([
                    student_university_name[students[i]][university_names[k]].Not(),
                    student_university_name[students[j]][university_names[k]].Not()])
                # Every student has a different/unique course
                model.AddBoolOr([
                    student_course[students[i]][courses[k]].Not(),
                    student_course[students[j]][courses[k]].Not()])

    #  There are two girls and two boys - condition is applied based on names
    # Carol and Elisa are assumed to be girls and Lucas and oliver are assumed to be boys
    model.AddBoolAnd([
        student_student_gender["Carol"]["Girl"],
        student_student_gender["Elisa"]["Girl"]])
    model.AddBoolAnd([
        student_student_gender["Carol"]["Boy"].Not(),
        student_student_gender["Elisa"]["Boy"].Not()])

    model.AddBoolAnd([
        student_student_gender["Oliver"]["Boy"],
        student_student_gender["Lucas"]["Boy"]])

    model.AddBoolAnd([
        student_student_gender["Oliver"]["Girl"].Not(),
        student_student_gender["Lucas"]["Girl"].Not()])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    print(solver.StatusName(status))

    solver.SearchForAllSolutions(model, SolutionPrinter_1(student_university_name, student_nationality, student_course,
                                                          student_student_gender ))

    for student in students:
        if solver.Value(student_course[student]["Architecture"]):
            for nationality in nationalities:
                if solver.Value(student_nationality[student][nationality]):
                    print("The student from " + nationality + " studies Architecture.")


task_1()
########################################################################################
print("################################################################################")
print("################################################################################")
print("#########################       Task : 1 End   #################################")
print("################################################################################")
print("################################################################################")
########################################################################################


########################################################################################
print("################################################################################")
print("################################################################################")
print("#########################       Task : 2       #################################")
print("################################################################################")
print("################################################################################")
########################################################################################

import numpy as np
import pandas as pd


class SolutionPrinter_2(cp_model.CpSolverSolutionCallback):
    def __init__(self, sudoku_size, empty_value):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.solutions_ = 0
        self.sudoku_grid_size = sudoku_size
        self.sudoku_value = empty_value

    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        print("solution", self.solutions_)
        result = np.zeros((self.sudoku_grid_size, self.sudoku_grid_size)).astype(int)
        for i in range(self.sudoku_grid_size):
            for j in range(self.sudoku_grid_size):
                result[i, j] = int(self.Value(self.sudoku_value[i, j]))
        print("*************************")
        print(result)
        print("*************************")






def sudoku_solve():
    data = {'puzzle': ["000000030705020000090000400000004002059600008300010050570060100000300000600400005"],
            'solution': [0]}
    sudoku = pd.DataFrame(data=data)
    sample = sudoku.loc[0]  # row 2020

    ## Transform an encoded puzzle into an integer matrix
    def string_conversion_into_matrix(sample: str):
        return np.matrix([np.array(list(sample[i:i + 9])).astype(int) for i in range(0, len(sample), 9)])

    sudoku_array = string_conversion_into_matrix(sample['puzzle'])
    print("Given Sudoku Problem : - \n")
    print(sudoku_array)

    def solve_model(sudoku_grid: np.matrix):
        assert sudoku_grid.shape == (9, 9)
        sudoku_grid_size = 9
        region_size = 3

        # Initialize Model
        model = cp_model.CpModel()

        # Initialize variables.
        x = {}
        for i in range(sudoku_grid_size):
            for j in range(sudoku_grid_size):
                if sudoku_grid[i, j] != 0:
                    # Initial values (values already defined on the puzzle).
                    x[i, j] = sudoku_grid[i, j]
                else:
                    x[i, j] = model.NewIntVar(1, sudoku_grid_size,
                                              'x[{},{}]'.format(i, j))  # Values to be found (variyng from 1 to 9).

        # Values constraints.
        # All elements of all rows must be different.
        for i in range(sudoku_grid_size):
            model.AddAllDifferent([x[i, j] for j in range(sudoku_grid_size)])

        # All elements of all columns must be different.
        for j in range(sudoku_grid_size):
            model.AddAllDifferent([x[i, j] for i in range(sudoku_grid_size)])

        # All elements of all regions must be different.
        for row_id in range(0, sudoku_grid_size, region_size):
            for col_id in range(0, sudoku_grid_size, region_size):
                model.AddAllDifferent(
                    [x[row_id + i, j] for j in range(col_id, (col_id + region_size)) for i in range(region_size)])

        solver = cp_model.CpSolver()
        solver.SearchForAllSolutions(model, SolutionPrinter_2(sudoku_grid_size, x))

    solve_model(sudoku_array)


sudoku_solve()
########################################################################################
print("################################################################################")
print("################################################################################")
print("#########################     Task : 2 End     #################################")
print("################################################################################")
print("################################################################################")
########################################################################################


########################################################################################
print("################################################################################")
print("################################################################################")
print("#########################       Task : 3       #################################")
print("################################################################################")
print("################################################################################")
########################################################################################
from ortools.sat.python import cp_model

# A. Load Data from Excel and extract all relevant information
Excel = pd.ExcelFile('Assignment_DA_1_data.xlsx')
projects_data = pd.read_excel(Excel, 'Projects')
quotes_data = pd.read_excel(Excel, 'Quotes')
dependencies_data = pd.read_excel(Excel, 'Dependencies')
value_data = pd.read_excel(Excel, 'Value')

# stored important information in list
projects = projects_data.iloc[:, 0].tolist()
month_list = projects_data.columns[1:].values.tolist()
contractors = quotes_data.iloc[:, 0].tolist()
job_list = quotes_data.columns[1:].values.tolist()
values = value_data["Value"].values.tolist()
project_dependencies = {}

# Initialize Model
model = cp_model.CpModel()

# declare list and dictionary that will be used further
project_values = {}
project_selected = {}
contractor_selected = {}
project_quotes = []
solution = []
proj_month_contractor_dict = {}
proj_month_contractor__value_dict = {}


# Solution printer class is defined for retrieving all possible soltuion
class SolutionPrinter_3(cp_model.CpSolverSolutionCallback):
    '''This class is just for printing all possible solutions'''

    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.solutions_ = 0
        self.outputs=[]

    # for count for all solution
    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        self.outputs.append(self.solutions_)

    def print_total_solutions(self):
        print("Number of possible solutions: ", len(self.outputs))


# Dict for mapping of project and value
for row in range(len(values)):
    project_values[value_data.iloc[row, 0]] = int(value_data.iloc[row, 1])

# B.Identify and create the decision variables in a CP-SAT model
# decision variables -  project_selected , contractor_selected
for project in range(len(projects)):
    project_month = {}
    for month in month_list:
        job = projects_data.iloc[project][month]
        month_contractor_list = []
        if job in job_list:
            for contractor in range(len(quotes_data[job])):
                cost = quotes_data[job][contractor]
                if not pd.isnull(quotes_data[job][contractor]):
                    contractor_tuple = (projects_data.iloc[project, 0], month, contractors[contractor], cost)
                    contractor_selected[contractor_tuple[:-1]] = model.NewBoolVar("x_%s_%s_%s" % contractor_tuple[:-1])
                    project_quotes.append(contractor_tuple)
                    month_contractor_list.append(contractors[contractor])
                    proj_month_contractor__value_dict[contractor_tuple[:-1]] = int(contractor_tuple[-1])
        if len(month_contractor_list) > 0:
            project_month[month] = month_contractor_list
    proj_month_contractor_dict[projects[project]] = project_month
    project_selected[projects[project]] = model.NewBoolVar('x_%s' % projects[project])

# C. a contractor cannot work on two projects simultaneously
# Reference source - https://developers.google.com/optimization/scheduling/employee_scheduling
# For example - It requires that each nurse works at most one shift per day.
# for n in all_nurses:
#   for d in all_days:
#       model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 1)
# For each nurse, the sum of shifts assigned to that nurse is at most 1 ("at most" because a nurse might have the day off).

for contractor in range(len(contractors)):
    for month in range(len(month_list)):
        model.Add(sum(
            [contractor_selected.get((projects[project], month_list[month], contractors[contractor]), False) for project
             in range(len(projects))]) <= 1)

# D. A project is accepted to be delivered then exactly one contractor per job of the project needs to work on it
for project in proj_month_contractor_dict:
    for month in proj_month_contractor_dict[project]:
        model.Add(sum([contractor_selected[(project, month, contractor)] for contractor in
                       proj_month_contractor_dict[project][month]]) == 1).OnlyEnforceIf(project_selected[project])

# E. A project is not taken on then no one should be contracted to work on it
for project in proj_month_contractor_dict:
    pmc_list = []
    for month in proj_month_contractor_dict[project]:
        for contractor in proj_month_contractor_dict[project][month]:
            pmc_list.append((project, month, contractor))
    model.AddBoolAnd([contractor_selected[element].Not() for element in pmc_list]).OnlyEnforceIf(
        project_selected[project].Not())

# F. the project dependency constraints
# Mapping projects with dependent projects
for project in range(len(projects)):
    project_row = dependencies_data.iloc[project]
    list_dependency = []
    for n in projects:
        if project_row[n] == 'x':
            list_dependency.append(n)
    project_dependencies[projects[project]] = list_dependency

# Linear Expression - Dependent project is selected only when the project has been selected already
for project in project_dependencies:
    if len(project_dependencies[project]) > 0:
        model.AddBoolAnd(
            [project_selected[project_name] for project_name in project_dependencies[project]]).OnlyEnforceIf(
            project_selected[project])

# G. the constraint that the profit margin
# Created linear expression between project * value and selected contractor * quote
model.Add(sum([(project_values[project] * project_selected[project]) -
               sum([proj_month_contractor__value_dict[(project, month, contractor)]
                    * contractor_selected[(project, month, contractor)]
                    for month in proj_month_contractor_dict[project]
                    for contractor in proj_month_contractor_dict[project][month]])
               for project in projects]) >= 2500)

# H. Solve the CP-SAT model and determine how many possible solutions satisfy all constraints
solver = cp_model.CpSolver()
result = solver.Solve(model)
solution_printer = SolutionPrinter_3()
status = solver.SearchForAllSolutions(model, solution_printer)
print("Solution Status : ", solver.StatusName(result))

selected_projects = []
totalValue_selected_project = 0
totalCost_selected_project = 0
proj_contractor_month_list = []

# Iterate selected project and contractor with respect to month
for project in proj_month_contractor_dict:
    if solver.Value(project_selected[project]):
        totalValue_selected_project += project_values[project]
        selected_projects.append(project)
        for month in proj_month_contractor_dict[project]:
            for contractor in proj_month_contractor_dict[project][month]:
                if solver.Value(contractor_selected[(project, month, contractor)]):
                    proj_month_contractor_sep_list = project + "," + month + "," + contractor
                    proj_contractor_month_list.append(proj_month_contractor_sep_list)
                    totalCost_selected_project += proj_month_contractor__value_dict[(project, month, contractor)]

# Profit margin for selected project
profit_margin = totalValue_selected_project - totalCost_selected_project
solution.append([proj_contractor_month_list, selected_projects, totalCost_selected_project, totalValue_selected_project,
                 profit_margin])

# Saved output in Excel file
solution_printer.print_total_solutions()
print("final result is saved in solution.csv file")
with open("solution.csv", 'w') as f:
    for project_contractor in solution[0][0]:
        f.write(project_contractor + "\n")
    f.write("\nProjects_considered_for_profit_margin : " + str(solution[0][1]) + "\n")
    f.write(" Cost: " + str(solution[0][2]) + "\n")
    f.write(" Value: " + str(solution[0][3]) + "\n")
    f.write("Profit Margin: " + str(solution[0][4]) + "\n")

########################################################################################
print("################################################################################")
print("################################################################################")
print("#########################       Task : 3 End      ##############################")
print("################################################################################")
print("################################################################################")
########################################################################################
