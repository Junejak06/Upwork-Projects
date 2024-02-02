import pandas as pd

def process_match_data(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Initialize variables to track the current match and store results
    current_match = None
    processed_data = []

    for index, row in df.iterrows():
        match_key = (row['Home Team'], row['Away Team'])
        goal_time_str = row['Goal Time'].replace("'", "").split('+')[0]
        goal_time = int(goal_time_str)
        goal_score = row['Goal Score']

        if match_key != current_match:
            # If this is a new match, save the previous match data and start a new match count
            if current_match is not None:
                processed_data.append(process_match_result(current_match, match_goals, match_scores, fh_goals, sh_goals))

            current_match = match_key
            match_goals = []
            match_scores = []
            fh_goals, sh_goals = 0, 0

        # Store goal times and scores for the current match
        match_goals.append(goal_time)
        match_scores.append(goal_score)

        # Count goals for the current match in each half
        if goal_time <= 45 or '45+' in row['Goal Time']:
            fh_goals += 1
        else:
            sh_goals += 1

    # Add the last match
    processed_data.append(process_match_result(current_match, match_goals, match_scores, fh_goals, sh_goals))

    # Convert the processed data to a DataFrame with rearranged columns
    output_df = pd.DataFrame(processed_data, columns=[
        'Home Team', 'Away Team', 'FH Goals', 'SH Goals', 
        '20 Min Score', 'Goals Scored (20)', '1+ More Goals By FT (20)', '2+ More Goals By FT (20)', '3+ More Goals By FT (20)', '1+ More Goals By HT (20)',
        '30 Min Score', 'Goals Scored (30)', '1+ More Goals By FT (30)', '2+ More Goals By FT (30)', '3+ More Goals By FT (30)', '1+ More Goals By HT (30)',
        '60 Min Score', 'Goals Scored (60)', '1+ More Goals By FT (60)', '2+ More Goals By FT (60)',
        '70 Min Score', 'Goals Scored (70)', '1+ More Goals By FT (70)', '2+ More Goals By FT (70)',
        '80 Min Score', 'Goals Scored (80)', '1+ More Goals By FT (80)'
    ])

    # Change the data type of all columns to plain numbers (1 and 0)
    output_df = output_df.astype({col: int for col in output_df.columns if 'Goals' in col or 'By' in col})

    # Ensure that the score columns are consistently saved as plain text
    for minute in [20, 30, 60, 70, 80]:
        output_df[f'{minute} Min Score'] = output_df[f'{minute} Min Score'].str.replace(r'^\d+-\d+$', 'Plain Text')

    # Write the DataFrame to a CSV file
    output_df.to_csv(output_file, index=False)

def process_match_result(match_key, match_goals, match_scores, fh_goals, sh_goals):
    home_team, away_team = match_key

    # Initialize scores at different minute marks and their corresponding goals after that minute
    score_at_minutes = {minute: '0 - 0' for minute in [20, 30, 60, 70, 80]}
    goals_after_minutes = {minute: 0 for minute in [20, 30, 60, 70, 80]}
    goals_by_ft = {minute: [False, False, False] for minute in [20, 30]}
    goals_by_ft_60_70 = {minute: [False, False] for minute in [60, 70]}
    goals_by_ft_80 = [False]

    for time, score in zip(match_goals, match_scores):
        for minute in [20, 30, 60, 70, 80]:
            if time <= minute:
                score_at_minutes[minute] = score
            goals_after_minutes[minute] = sum(t > minute for t in match_goals)

    # Calculate additional columns for each minute mark
    for minute in [20, 30]:
        goals_by_ft[minute] = [goals_after_minutes[minute] >= i for i in range(1, 4)]
    for minute in [60, 70]:
        goals_by_ft_60_70[minute] = [goals_after_minutes[minute] >= i for i in range(1, 3)]
    goals_by_ft_80 = [goals_after_minutes[80] >= 1]

    # Construct the final row for this match
    row_data = [home_team, away_team, fh_goals, sh_goals]
    for minute in [20, 30]:
        row_data.extend([score_at_minutes[minute], sum(t <= minute for t in match_goals)] + goals_by_ft[minute] + [len([time for time in match_goals if minute < time <= 45]) >= 1])
    for minute in [60, 70]:
        row_data.extend([score_at_minutes[minute], sum(t <= minute for t in match_goals)] + goals_by_ft_60_70[minute])
    row_data.extend([score_at_minutes[80], sum(t <= 80 for t in match_goals)] + goals_by_ft_80)

    return row_data

# Example Usage
process_match_data('match_goals_details_10.csv', 'output_file14.csv')
