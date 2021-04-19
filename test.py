jobs_data = [  # task = (machine_id, processing_time).
        [(0, 3), (1, 2), (2, 2)],  # Job0
        [(0, 2), (2, 1), (1, 4)],  # Job1
        [(1, 4), (2, 3)]  # Job2
    ]
machines_count=[]
for job in jobs_data:
    for task in job:
        machines_count.append(task[0])

print(max(machines_count))
# machines_count = 1 + max(task[0] for job in jobs_data for task in job)
# all_machines = range(machines_count)