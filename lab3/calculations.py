import re
from datetime import timedelta

def parse_time(time_str):
    if not time_str or time_str == "--":
        return None
    parts = list(map(int, time_str.split(':')))
    return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])

def calculate_metrics(file_path):
    total_cpu_seconds = 0
    total_wall_seconds = 0
    efficiencies_list = []
    job_count = 0
    CORES_PER_JOB = 4 

    time_pattern = re.compile(r'\d{2,}:\d{2}:\d{2}')
    eff_pattern = re.compile(r'(\d+\.\d+)%')
    
    with open(file_path, 'r') as file:
        for line in file:
            if "blender-job" in line:
                times = time_pattern.findall(line)
                pct_matches = eff_pattern.findall(line)
                
                if len(times) >= 2 and len(pct_matches) >= 2:
                    cpu_val = parse_time(times[0])
                    wall_val = parse_time(times[1])
                    
                    eff_val = float(pct_matches[1])
                    
                    if cpu_val and wall_val:
                        total_cpu_seconds += cpu_val.total_seconds()
                        total_wall_seconds += wall_val.total_seconds()
                        efficiencies_list.append(eff_val)
                        job_count += 1

    if job_count == 0:
        return 0, 0, 0, 0

    avg_column_eff = sum(efficiencies_list) / job_count
    total_aggregate_eff = (total_cpu_seconds / (total_wall_seconds * CORES_PER_JOB)) * 100
    total_cpu_hours = total_cpu_seconds / 3600
    
    return total_cpu_hours, avg_column_eff, total_aggregate_eff, job_count

file_name = "jobs.txt"
try:
    cpu_hrs, avg_eff, total_eff, count = calculate_metrics(file_name)
    print(f"Number of analyzed frames (jobs): {count}")
    print(f"Total computational cost: {cpu_hrs:.2f} CPU-hours")
    print(f"Average efficiency (corrected Eff. column): {avg_eff:.2f}%")
    print(f"Total aggregate efficiency (calculated): {total_eff:.2f}%")
except Exception as e:
    print(f"Error: {e}")