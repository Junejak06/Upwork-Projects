import csv
import math
import os


# Constants
A = 20  # A-value (recency and importance)
LEAGUES_TO_PROCESS = ["LPL", "LCK", "LCS", "LEC", "PCS", "VCS", "LJL", "CBLOL", "LLA", "MSI", "WLDs", "WCS"]

def elo_rating(Rold_T, Rold_Top, M, S, I):
    E_T = 1 / (1 + 10 ** ((Rold_Top - Rold_T) / 400))  # Team’s expected result of the match
    R_new_T = Rold_T + A * I * M * (S - E_T)
    return R_new_T

def margin_of_victory(G, Rold_Twin, Rold_Tloss):
    return math.log((abs(G) + 0.0262) * 38.171) * (2.2 / (0.001 * (Rold_Twin - Rold_Tloss) + 2.2))

teams_ratings = {}
teams_regions = {}

with open('2023_LoL_esports_match_data_from_OraclesElixir.csv', 'r', encoding='latin-1') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # Skip header

    for row in csv_reader:
        league = row[3]
        position = row[12]

        if league not in LEAGUES_TO_PROCESS:
            continue

        if position == "team":
            team_name_1 = row[15]
            S_1 = int(row[24])
            G_1 = float(row[86])

            # Set default initial rating for team 1
            Rold_1 = teams_ratings.get(team_name_1, 1370 if league not in ["LPL", "LCK", "LCS", "LEC"] else 1600 if league in ["LPL", "LCK"] else 1520)

            # Fetch the second team details from the next row
            next_row = next(csv_reader)
            team_name_2 = next_row[15]
            S_2 = int(next_row[24])
            G_2 = float(next_row[86])

            # Set default initial rating for team 2
            Rold_2 = teams_ratings.get(team_name_2, 1370 if league not in ["LPL", "LCK", "LCS", "LEC"] else 1600 if league in ["LPL", "LCK"] else 1520)

            # Match importance
            I = 1.0
            if league == "MSI":
                I = 1.25
            elif league == "WCS":
                I = 1.75

            # Margin of victory calculations
            M_1 = margin_of_victory(G_1, Rold_1, Rold_2)
            M_2 = margin_of_victory(G_2, Rold_2, Rold_1)

            # Calculate new ratings for both teams
            Rnew_1 = elo_rating(Rold_1, Rold_2, M_1, S_1, I)
            Rnew_2 = elo_rating(Rold_2, Rold_1, M_2, S_2, I)

            teams_ratings[team_name_1] = Rnew_1
            teams_ratings[team_name_2] = Rnew_2

            # Store regions for teams
            teams_regions[team_name_1] = teams_regions.get(team_name_1, [])
            if league not in teams_regions[team_name_1]:
                teams_regions[team_name_1].append(league)

            teams_regions[team_name_2] = teams_regions.get(team_name_2, [])
            if league not in teams_regions[team_name_2]:
                teams_regions[team_name_2].append(league)

if not os.path.exists('updated_ratings.csv'):
    with open('updated_ratings.csv', 'w') as f:
        pass

with open('updated_ratings.csv', 'w', newline='') as csv_output:
    csv_writer = csv.writer(csv_output)
    csv_writer.writerow(["Region", "Team Name", "Rating"])

    for team, rating in teams_ratings.items():
        regions = "/".join(teams_regions[team])
        print(f"Region: {regions}, Team Name: {team} Rating: {round(rating, 2)}")
        csv_writer.writerow([regions, team, round(rating, 2)])
