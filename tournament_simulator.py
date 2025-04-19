import random
from collections import defaultdict

# --- Constants ---
DEFAULT_UNRATED_SIM_RATING = 1400 # Rating assigned to unrated players for simulation

def find_best_opponent(player1_id, potential_opponents_ids, players_data):
    """Finds the best opponent for player1_id from the list of potential_opponents_ids.

    Prioritizes:
    1. Opponent not played before.
    2. Closest number of wins.
    If no new opponent is available, allows rematches, still prioritizing closest wins.
    """
    if not potential_opponents_ids:
        return None

    p1_wins = players_data[player1_id]["wins"]
    p1_played = players_data[player1_id]["played"]
    best_match_id = None
    found_new_opponent = False

    sorted_opponents = sorted(
        potential_opponents_ids,
        key=lambda opp_id: abs(players_data[opp_id]["wins"] - p1_wins)
    )

    # Attempt 1: Find best NEW opponent
    for p2_id in sorted_opponents:
        if p2_id not in p1_played:
            best_match_id = p2_id
            found_new_opponent = True
            break

    # Attempt 2: If no new opponent, find best REMATCH opponent
    if not found_new_opponent and sorted_opponents:
        best_match_id = sorted_opponents[0]

    return best_match_id

def simulate_match_result(p1_id, p2_id, players_data):
    """Simulates the result of a match based on player ratings."""
    r1 = players_data[p1_id]["rating"] if players_data[p1_id]["rating"] is not None else DEFAULT_UNRATED_SIM_RATING
    r2 = players_data[p2_id]["rating"] if players_data[p2_id]["rating"] is not None else DEFAULT_UNRATED_SIM_RATING

    rating_diff = r1 - r2

    # --- Define Probabilities based on rating difference ---
    # These probabilities are examples and can be tuned
    if abs(rating_diff) > 300: # Significant difference
        prob_p1_win = 0.80 if rating_diff > 0 else 0.10
        prob_draw = 0.10
    elif abs(rating_diff) > 100: # Moderate difference
        prob_p1_win = 0.65 if rating_diff > 0 else 0.20
        prob_draw = 0.15
    else: # Close ratings
        prob_p1_win = 0.40 # Slightly less than 50% to account for draw chance
        prob_draw = 0.20

    # Ensure probabilities sum roughly to 1
    prob_p2_win = 1.0 - prob_p1_win - prob_draw
    if prob_p2_win < 0: # Basic sanity check / adjustment
        prob_p2_win = 0
        prob_draw = 1.0 - prob_p1_win # Adjust draw prob if p2_win goes negative

    # Possible outcomes and their probabilities
    outcomes = [p1_id, p2_id, 'draw']
    probabilities = [prob_p1_win, prob_p2_win, prob_draw]

    # Choose an outcome based on the probabilities
    result = random.choices(outcomes, weights=probabilities, k=1)[0]
    return result


def simulate_chess_tournament(num_players=10, num_rounds=3, rated_percentage=0.8):
    """Simulates a chess tournament non-interactively after setup.

    Args:
        num_players (int): The number of players in the tournament.
        num_rounds (int): The number of rounds in the tournament.
        rated_percentage (float): Probability for each player to get a rating (0.0 to 1.0).

    Returns:
        dict: A dictionary containing the final results of the tournament.
    """
    # --- Input Validation ---
    if not isinstance(num_players, int) or num_players < 2:
        print("Error: Number of players must be an integer >= 2.")
        return None
    if not isinstance(num_rounds, int) or num_rounds < 1:
        print("Error: Number of rounds must be an integer >= 1.")
        return None
    if not isinstance(rated_percentage, (float, int)) or not (0.0 <= rated_percentage <= 1.0):
        print("Error: Rated percentage must be a number between 0.0 and 1.0.")
        return None
    # --- End Input Validation ---

    # --- Player Initialization (Non-Deterministic Rating) ---
    players = {}
    actual_rated_count = 0
    for i in range(1, num_players + 1):
        rating = None
        is_rated = random.random() < rated_percentage
        if is_rated:
            rating = random.randint(1000, 2000)
            actual_rated_count += 1
        players[i] = {"rating": rating, "wins": 0, "losses": 0, "draws": 0, "played": set()}
    print(f"(Initialized players: {actual_rated_count} of {num_players} assigned ratings non-deterministically)")
    # --- End Player Initialization ---

    tournament_history = defaultdict(list) # Store list of (p1, p2) pairs per round
    bye_player_id = None # Track player with bye in the current round

    print(f"\nStarting Simulation: {num_players} players, {num_rounds} rounds ({rated_percentage*100:.0f}% target rated)")

    # --- Main Round Loop ---
    for round_num in range(1, num_rounds + 1):
        print(f"\n--- Simulating Round {round_num} ---")
        round_pairings_list = []
        paired_ids_this_round = set()
        bye_player_id = None

        # --- Pairing Logic (same as before) ---
        unpaired_players_ids = list(players.keys())
        random.shuffle(unpaired_players_ids)
        unpaired_players_ids.sort(key=lambda pid: players[pid]["wins"], reverse=True)
        players_to_pair = list(unpaired_players_ids)

        while len(players_to_pair) >= 2:
            p1_id = players_to_pair.pop(0)
            potential_opponents = list(players_to_pair)
            if not potential_opponents:
                players_to_pair.insert(0, p1_id)
                break
            p2_id = find_best_opponent(p1_id, potential_opponents, players)
            if p2_id:
                pair = tuple(sorted((p1_id, p2_id)))
                round_pairings_list.append(pair)
                players[p1_id]["played"].add(p2_id)
                players[p2_id]["played"].add(p1_id)
                paired_ids_this_round.add(p1_id)
                paired_ids_this_round.add(p2_id)
                players_to_pair.remove(p2_id)
            else:
                print(f"Warning: Could not find opponent for {p1_id}?")
                players_to_pair.insert(0, p1_id)

        # --- Check for Bye ---
        if len(players_to_pair) == 1:
            bye_player_id = players_to_pair[0]
            print(f"Player {bye_player_id} has a bye this round.")
            # Optional: Grant bye point if desired
            # players[bye_player_id]["wins"] += 1 # Or use a separate 'byes' counter
        elif len(players_to_pair) > 1:
            print(f"ERROR: Pairing logic failed. Unpaired: {players_to_pair}")

        tournament_history[round_num] = round_pairings_list

        # --- Display Pairings for the Round ---
        print("Pairings for this round:")
        displayed_matches = set() # Use set of sorted tuples
        if not round_pairings_list:
            print("  No matches played this round.")
        else:
            for p1, p2 in round_pairings_list:
                rating_info_p1 = f"(R:{players[p1]['rating']})" if players[p1]['rating'] is not None else f"(U, W:{players[p1]['wins']})"
                rating_info_p2 = f"(R:{players[p2]['rating']})" if players[p2]['rating'] is not None else f"(U, W:{players[p2]['wins']})"
                print(f"  {p1} {rating_info_p1} vs {p2} {rating_info_p2}")
                displayed_matches.add(tuple(sorted((p1, p2))))

        # --- Simulate Results & Update Scores ---
        print("Simulated Results:")
        if not displayed_matches:
             print("  No results to simulate.")
        else:
            for p1, p2 in displayed_matches: # Iterate through the canonical pairs
                result = simulate_match_result(p1, p2, players)

                # Update scores based on simulated result
                if result == p1:
                    print(f"  Match: {p1} defeats {p2}")
                    players[p1]["wins"] += 1
                    players[p2]["losses"] += 1
                elif result == p2:
                    print(f"  Match: {p2} defeats {p1}")
                    players[p2]["wins"] += 1
                    players[p1]["losses"] += 1
                elif result == 'draw':
                    print(f"  Match: {p1} draws {p2}")
                    players[p1]["draws"] += 1
                    players[p2]["draws"] += 1
                else:
                    print(f"  Warning: Unknown simulation result for {p1} vs {p2}")

        print(f"--- End of Simulated Round {round_num} ---")
    # --- End of Round Loop ---

    print("\n--- Simulation Finished ---")
    print("\nFinal Player Records:")
    # Sort players by points (Win=1, Draw=0.5) descending for final standings
    sorted_player_ids = sorted(
        players.keys(),
        key=lambda pid: (players[pid]["wins"] + 0.5 * players[pid]["draws"]),
        reverse=True
    )
    for player_id in sorted_player_ids:
        data = players[player_id]
        rating_info = f"(Rated: {data['rating']})" if data['rating'] is not None else "(Unrated)"
        points = data['wins'] + 0.5 * data['draws']
        print(f"Player {player_id} {rating_info}: Points={points:.1f} (W:{data['wins']}, L:{data['losses']}, D:{data['draws']})")

    # Return the final state
    return {"players": players, "history": dict(tournament_history)}


# ==================================================
# Main execution block - Handles User Input for Setup
# ==================================================
if __name__ == "__main__":
    print("--- Chess Tournament Simulator Setup ---")

    # Get number of players from user input
    while True:
        try:
            num_players_str = input("Enter the total number of players (must be at least 2): ")
            num_players = int(num_players_str)
            if num_players >= 2:
                break
            else:
                print("Number of players must be at least 2.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    # Get number of rounds from user input
    while True:
        try:
            num_rounds_str = input("Enter the number of rounds (must be at least 1): ")
            num_rounds = int(num_rounds_str)
            if num_rounds >= 1:
                break
            else:
                print("Number of rounds must be at least 1.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    # Get rated percentage from user input
    while True:
        try:
            rated_percentage_str = input("Enter the percentage of rated players (between 0.0 and 1.0, e.g., 0.75 for 75%): ")
            rated_percentage = float(rated_percentage_str)
            if 0.0 <= rated_percentage <= 1.0:
                break
            else:
                print("Rated percentage must be between 0.0 and 1.0.")
        except ValueError:
            print("Invalid input. Please enter a number (like 0.8 or 0).")

    # Call the main simulation function with user-provided values
    tournament_results = simulate_chess_tournament(
        num_players=num_players,
        num_rounds=num_rounds,
        rated_percentage=rated_percentage
    )

    if tournament_results:
        print("\n--- Tournament Simulation Complete ---")
    else:
        print("\n--- Tournament Simulation Failed (Input Error?) ---")
