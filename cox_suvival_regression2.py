import pandas as pd
#from lifelines import CoxPHFitter
from lifelines import CoxTimeVaryingFitter

# Example data
df = pd.DataFrame([
    {"person_id": 1, "session_date": "2024-04-10", "sale_date": "2024-05-15", "data_end_date": "2024-12-31"},
    {"person_id": 2, "session_date": "2024-06-01", "sale_date": None, "data_end_date": "2024-12-31"},
    {"person_id": 3, "session_date": "2024-03-20", "sale_date": "2024-07-05", "data_end_date": "2024-12-31"},
    ])

# Convert to datetime
for col in ["session_date", "sale_date", "data_end_date"]:
    df[col] = pd.to_datetime(df[col])

# Reference start date for counting days
ref_date = df[["session_date", "sale_date", "data_end_date"]].stack().min()

rows = []

for _, r in df.iterrows():
    pid = r["person_id"]
    session = r["session_date"]
    sale = r["sale_date"]
    obs_end = r["data_end_date"]

    # Cap end date at 3 months after session
    cap_date = session + pd.Timedelta(days=90)
    final_end_date = min(cap_date, obs_end)

    # If sale exists, make sure we stop at sale
    if pd.notna(sale) and sale <= final_end_date:
        event_date = sale
        event_flag = 1
    else:
        event_date = final_end_date
        event_flag = 0

    # Convert all to numeric days from ref_date
    s_days = (session - ref_date).days
    event_days = (event_date - ref_date).days

    # event before study session.
    if s_days > 0:
        rows.append({
            "person_id": pid,
            "start": 0,
            "stop": min(s_days, event_days),
            "event": 1 if (event_days <= s_days and event_flag == 1) else 0,
            "post_session": 0
            })

    # event after study session.
    if event_days > s_days:
        rows.append({
            "person_id": pid,
            "start": s_days,
            "stop": event_days,
            "event": 1 if (event_days > s_days and event_flag == 1) else 0,
            "post_session": 1
            })

tv_df = pd.DataFrame(rows)
'''
start: study session date respect to reference date.
stop: Either sales date or simulation end date respect to reference date.
event: sales happened or not.
post_session: period either before(0) or after(1) study session.
 
The coefficient for post_session in the Cox model tells you 
whether hazard of sale is higher in the post period.
exp(coef) = 2.0 means sales is extimated to be twice as high in post study session.
'''

# Fit Cox model with time-varying covariate
ctv = CoxTimeVaryingFitter()
ctv.fit(tv_df, id_col="person_id", start_col="start", stop_col="stop", event_col="event")
ctv.print_summary()
