# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 21:00:35 2021

@author: Tanvi
"""


from ortools.sat.python import cp_model
import numpy as np
import pandas as pd

# A. Load the excel file Assignment_DA_1_data.xlsx and extract all relevant information [1 point]. 
# Make sure to use the data from the file in your code, please do not hardcode any values that can be read
# from the file.

xlsx = pd.ExcelFile('Assignment_DA_1_data.xlsx')
projects_df = pd.read_excel(xlsx, 'Projects')
quotes_df = pd.read_excel(xlsx, 'Quotes')
dependencies_df = pd.read_excel(xlsx, 'Dependencies')
value_df = pd.read_excel(xlsx, 'Value')

#lists
projects = projects_df["Unnamed: 0"].values.tolist()
months = projects_df.columns[1:].values.tolist()
contractors = quotes_df["Unnamed: 0"].values.tolist()
jobs = quotes_df.columns[1:].values.tolist()
values = value_df["Value"].values.tolist()
dependencies={}


# Initializing Cp model
model = cp_model.CpModel()

# Reading project dependencies corresponding to x
for project in range(len(projects)):
    project_row = dependencies_df.iloc[project]
    list_dependency = []
    for n in projects:
        if(project_row[n]=='x'):
            list_dependency.append(n)
    
    dependencies[projects[project]] = list_dependency


# B. Identify and create the decision variables in a CP-SAT model that you need to decide projects to 
# take on [1 point]. 
# Also identify and create the decision variables you need to decide, which contractor is working on 
# which project and when. Make sure to consider that not all contractors are qualified 
# to work on all jobs and that projects do not run over all months [3 points].

# Dictionary with key as project and value as value
projectValues = {}

# Dictionary with key as project and value as boolean if the project is chosen
projectsChosen = {}

# Dictionary with key as contractor and value as boolean if the contractor is chosen for a job in a month
contractorsChosen = {}

# Project Quotes is a tuple of (project, month, contractor, cost)
projectQuotes = []

# Final solutions
finalSolution = []

# Creating a variable that will store Project + Month + Contractor relation
pmc_dict = {}

# Creating a variable that will store for each job Project + Month + Contractor + Quote relation
pmcv_dict = {}

def write_solution(solutions):
    
    with open("Output.csv", 'w') as f:
        for solution in solutions:
            f.write("Solution #: ,"+ str(solution[0])+"\n")
            for contractor_per_project in solution[1]:
                f.write(contractor_per_project+"\n")
            f.write("\nProjects Selected :,"+str(solution[2])+"\n")
            f.write("Total Cost: ,"+str(solution[3])+"\n")
            f.write("Project Value: ,"+str(solution[4])+"\n")
            f.write("Profit Margin: ,"+str(solution[5])+"\n\n")

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    '''This class is just for printing all possible solutions'''
    def __init__(self, projects, pmc_dict):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.solutions_ = 0
        self.projects_ = projects
        self.pmc_dictionary = pmc_dict

    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        
        # List of projects selected
        selected_projects = []
        
        # Total value from shortlisted projects
        # Total cost for projects taken by contractors
        totalValue = totalCost = 0

        # project+contractor+month relation list of selected projects
        pcm_relation = []
        
        # collating/calculating parts of the final solution
        for project in pmc_dict:
            if self.Value(self.projects_[project]):
                
                # summation of value from selected projects 
                totalValue += projectValues[project]
                
                # extracting and appending selected projects from the dict
                selected_projects.append(project)
                
                for month in pmc_dict[project]:
                    for contractor in pmc_dict[project][month]:
                        
                        # creating comma-separated project,month,contractor
                        if self.Value(self.pmc_dictionary[(project, month, contractor)]):
                            comma_separated_pmc = project + "," + month + "," + contractor
                            pcm_relation.append(comma_separated_pmc)
                            
                            # value against a given project, month and contractor combination
                            totalCost += pmcv_dict[(project, month, contractor)]

        # Calculating profit margin (difference between sum of selected projects valuation and sum of selected contractors quote for a particular job)
        profit_margin = totalValue - totalCost
        finalSolution.append([self.solutions_, pcm_relation, selected_projects, totalCost, totalValue, profit_margin])
               
        
# Creating dictionary with key as project and value as value
for row in range(len(values)):
    projectValues[value_df.iloc[row,0]] = int(value_df.iloc[row,1])

# Below for loop creates:
# 1. decision variables:
# i. projectsChosen - whether a project is chosen or not
# ii. contractorsChosen - which contractor is working on which project and when
# 2. pmc_dict - relationship between project, month, contractor
# 3. pmcv_dict - relationship between project, month, contractor, contractor quote

for project in range(len(projects)):
    project_month = {}
    for month in months:
        job = projects_df.iloc[project][month]
        monthContractors = []
        if not (job != job):
            for contractor in range(len(quotes_df[job])):
                cost = quotes_df[job][contractor]
                if not (cost != cost):
                    contractor_tuple = (projects_df.iloc[project,0],month, contractors[contractor], cost)
                    contractorsChosen[contractor_tuple[:-1]] = model.NewBoolVar("x_%s_%s_%s" % contractor_tuple[:-1])
                    projectQuotes.append(contractor_tuple)
                    monthContractors.append(contractors[contractor])
                    pmcv_dict[contractor_tuple[:-1]] = int(contractor_tuple[-1])
        if len(monthContractors) != 0:
            project_month[month] = monthContractors
    pmc_dict[projects[project]] = project_month
    
    projectsChosen[projects[project]]  = model.NewBoolVar('x_%s'%projects[project])
    


# C. Define and implement the constraint that a contractor cannot work on two projects simultaneously [3 points]
for contractor in range(len(contractors)):
    for month in range(len(months)):
        # The contractor can work only for 1 or 0 projects.
        # If project,month,contractor get operation doesn't return, we assign false
        model.Add(sum([contractorsChosen.get((projects[project], months[month], contractors[contractor]), False) for project in range(len(projects))]) <= 1)

# D. Define and implement the constraint that if a project is accepted to be delivered 
# then exactly one contractor per job of the project needs to work on it [4 points]. 
for project in pmc_dict:
    for month in pmc_dict[project]:
        model.Add(sum([contractorsChosen[(project, month, contractor)] for contractor in pmc_dict[project][month]]) == 1).OnlyEnforceIf(projectsChosen[project])

# E. Define and implement the constraint that if a project is accepted
# to be delivered then exactly one contractor per job of the
# project needs to work on it [4 points]

for project in pmc_dict:
    pmc_tuple_list = []
    for month in pmc_dict[project]:
        for contractor in pmc_dict[project][month]:
            pmc_tuple_list.append((project, month, contractor))
    model.AddBoolAnd([contractorsChosen[element].Not() for element in pmc_tuple_list]).OnlyEnforceIf(projectsChosen[project].Not())

# F. Define and implement the project dependency constraint [2 points].

for project in dependencies:
    if len(dependencies[project]) != 0:
        model.AddBoolAnd([projectsChosen[project_name] for project_name in dependencies[project]]).OnlyEnforceIf(projectsChosen[project])

# G. Define and implement the constraint that the profit margin, i.e. the difference between 
# the value of all delivered projects and the cost of all required subcontractors, 
# is at least €2500 [5 points].

# Multiplying projectValues with projectsChosen 
# We are multiplying selected contractors with their quotes
# finally subtracting them and filtering profit_margin >=2500
model.Add(sum([(projectValues[project] * projectsChosen[project]) -
               sum([pmcv_dict[(project, month, contractor)]
                    * contractorsChosen[(project, month, contractor)]
                    for month in pmc_dict[project]
                    for contractor in pmc_dict[project][month]])
               for project in projects]) >= 2500)
                            
# CpSolver model object creation
solver = cp_model.CpSolver()
status = solver.SearchForAllSolutions(model, SolutionPrinter(projectsChosen, contractorsChosen))
#print(solver.StatusName(status))

# H. Solve the CP-SAT model and determine how many possible solutions satisfy all the constraints [1 point]. For each solution, determine what projects are taken on [1 point], which contractors work on which projects in which month [1 point], and what is the profit margin [1 point].
print("Total number of solutions are: ",len(finalSolution), ". Please open Output.csv for viewing solutions.")
write_solution(finalSolution) 
        
    


