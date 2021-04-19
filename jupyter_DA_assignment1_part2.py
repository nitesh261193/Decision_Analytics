from ortools.sat.python import cp_model
import pandas as pd
from collections import defaultdict

# Loading the project / quotes / dependencies / value sheets
xlsx = pd.ExcelFile('Assignment_DA_1_data.xlsx')
projects_df = pd.read_excel(xlsx, 'Projects')
quotes = pd.read_excel(xlsx, 'Quotes')
dependencies = pd.read_excel(xlsx, 'Dependencies')
value = pd.read_excel(xlsx, 'Value')

# Initilizing the Model
model = cp_model.CpModel()


dict_of_projects_per_contrac_and_month = defaultdict(list)
month_wise_dict_of_contractors = defaultdict(list)
eligible_contractor_for_jobs_dict = defaultdict(list)
dict_of_months_per_project_and_contractor = defaultdict(list)
eligible_contractor_for_jobs = {}
dict_of_projects_to_be_taken = {}
dictionary_of_month_contrac_quote_per_project = defaultdict(list)


#lists
projects = projects_df["Unnamed: 0"].values.tolist()
months = projects_df.columns[1:].values.tolist()
contractors = quotes["Unnamed: 0"].values.tolist()
jobs = quotes.columns[1:].values.tolist()
values = value["Value"].values.tolist()
dependency = {}


# Reading project dependencies corresponding to x
for project in range(len(projects)):
    project_row = dependencies.iloc[project]
    list_dependency = []
    for n in projects:
        if project_row[n] == 'x':
            list_dependency.append(n)

    dependency[projects[project]] = list_dependency

# Initialing Boolean Variable for every project that can be taken
for project in projects:
    dict_of_projects_to_be_taken[project] = model.NewBoolVar(project)

# Atleast one of the projects be taken
model.AddBoolOr([dict_of_projects_to_be_taken[project] for project in projects])

# Initialing Boolean Variable for every project , month and eligible contractors combination
for project in projects:
    for month in months:
        for contractor in contractors:
            # Ensure this key does not represent as NaN value in the project sheet
            if not pd.isnull(projects_df.iloc[project, month]):

                # Ensure this key does not represent as NaN value in the quotes sheet
                if not pd.isnull(quotes.loc[contractor, projects_df.iloc[project, month]]):
                    eligible_contractor_for_jobs[(project, month, contractor)] = model.NewBoolVar(
                        "%s_%s_%s" % (project, month, contractor))

                    print("%s_%s_%s" % (project, month, contractor))

                    # While creating these boolean variable store these values in different structures
                    # which will be used later 

                    # Dict of list eligible contractors for every (project, month)  key
                    eligible_contractor_for_jobs_dict[(project, month)].append(contractor)

                    # Dict of list project and contractor combination  for every ( month)  key
                    month_wise_dict_of_contractors[month].append([project, contractor])

                    quote = quotes.loc[contractor, projects.loc[project, month]]
                    dict_of_projects_per_contrac_and_month[(contractor, month)].append(project)
                    dict_of_months_per_project_and_contractor[(project, contractor)].append(month)
                    dictionary_of_month_contrac_quote_per_project[project].append([project, month, contractor, quote])

# only one of the eligible contractors gets the job

dictionary_of_quotes_per_project = defaultdict(list)

for project in projects:
    for month in projects.columns:
        for contractor in quotes.index:
            if not pd.isnull(projects.loc[project, month]):
                if not pd.isnull(quotes.loc[contractor, projects.loc[project, month]]):
                    # print('Helllo')
                    print(quotes.loc[contractor, projects.loc[project, month]])

                    dictionary_of_quotes_per_project[project].append(
                        quotes.loc[contractor, projects.loc[project, month]])

                    model.AddBoolAnd([eligible_contractor_for_jobs[(project, month, contrac)] for contrac in
                                     eligible_contractor_for_jobs_dict[(project, month)]])

# C. Define and implement the constraint that a contractor cannot work on two projects simultaneously [3 points]. 

my_list = []
cost_dict_per_project = defaultdict(list)
for project in projects:
    for month in projects.columns:
        for contractor in quotes.index:
            if not pd.isnull(projects.loc[project, month]):
                if not pd.isnull(quotes.loc[contractor, projects.loc[project, month]]):
                    # example: for the month of feb . contractor A can either work on project A or project B (Given that he is eligible)

                    model.AddBoolAnd([eligible_contractor_for_jobs[(p, month, contractor)] for p in
                                     dict_of_projects_per_contrac_and_month[contractor, month]])

                    # Append the Quotes of all the bids for each project
                    # Multiplying with the boolean variable will ensure that quotes from only shortlisted contracted are considered
                    # my_list.append (   eligible_contractor_for_jobs[(project, month, contractor)] * int(quote) )

# Define and implement the constraint that if a project is accepted to be delivered then
# exactly one contractor per job of the project needs to work on it [4 points]. 

for project in projects:
    for month in projects.columns:
        for contractor in quotes.index:
            if not pd.isnull(projects.loc[project, month]):
                if not pd.isnull(quotes.loc[contractor, projects.loc[project, month]]):
                    # For the Project A , if Contractor A is eligible to work in Month 1 and Month 3 : He can work only in one of the months.
                    model.AddBoolAnd([eligible_contractor_for_jobs[(project, m, contractor)] for m in
                                     dict_of_months_per_project_and_contractor[project, contractor]])

                # Ensure every project taken is profitable
over_all_cost_list = []
for project in projects:

    my_list = []
    for evry_combination in dictionary_of_month_contrac_quote_per_project[project]:
        project, month, contractor, quote = evry_combination

        # Append the Quotes of all the bids for each project
        # Multiplying with the boolean variable will ensure that quotes from only shortlisted contracters are considered
        my_list.append(eligible_contractor_for_jobs[(project, month, contractor)] * int(quote))

        # Similar as above but this is done to find the total sum of  all the projects short listed
        over_all_cost_list.append(eligible_contractor_for_jobs[(project, month, contractor)] * int(quote))

    total_cost_per_project = sum(my_list)

    # Find the value of the project that has been shortlisted
    # Multiplying with the boolean variable will ensure that value from only shortlisted projects are considered
    total_value_per_project = int(value.loc[project]) * dict_of_projects_to_be_taken[project]

    # Choose only the profitable projects
    if (total_cost_per_project < total_value_per_project):
        # print('Inside IF')
        model.AddBoolOr([dict_of_projects_to_be_taken[project]])

# Over all profit margin should be atleast 2500                    
over_all_cost = sum(over_all_cost_list)

my_list1 = []
for project in projects:
    my_list1.append(dict_of_projects_to_be_taken[project] * int(value.loc[project]))
overall_value = sum(my_list1)
maximum_budget = int(2500)

for project in dependencies:
    if len(dependencies[project]) != 0:
        model.AddBoolAnd([dict_of_projects_to_be_taken[project_name] for
                          project_name in dependencies[project]]).OnlyEnforceIf(dict_of_projects_to_be_taken[project])


solver = cp_model.CpSolver()

model.Maximize((overall_value - over_all_cost))
status = solver.Solve(model)
print(solver.StatusName(status))

# Writting the output on numpy arrays
final_result = pd.DataFrame(index=projects, columns=projects.columns)
final_result_with_quotes = pd.DataFrame(index=projects, columns=projects.columns)
project_month = {}

for project in projects:
    print(solver.Value(dict_of_projects_to_be_taken[project]))
    for month in projects.columns:
        for contractor in quotes.index:
            if not pd.isnull(projects.loc[project, month]):
                if not pd.isnull(quotes.loc[contractor, projects.loc[project, month]]):
                    if solver.Value(eligible_contractor_for_jobs[(project, month, contractor)]):
                        if solver.Value(dict_of_projects_to_be_taken[project]):
                            quote = quotes.loc[contractor, projects.loc[project, month]]
                            final_result.loc[project, month] = contractor
                            final_result_with_quotes.loc[project, month] = quote

# Writting the final output in the excel sheet
writer = pd.ExcelWriter("DA Ass1 part 2_output.xlsx")
final_result.to_excel(writer, sheet_name="projects", index=True)
final_result_with_quotes.to_excel(writer, sheet_name="quotes", index=True)
writer.close()
