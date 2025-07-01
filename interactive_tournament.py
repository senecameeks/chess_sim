import random
from collections import defaultdict

def find_best_opponent(player1_id, potential_opponents_ids, players_data):
    """Finds the best opponent for player1_id from the list of potential_opponents_ids.

    Prioritizes:
    1. Opponent not played before.
    2. Closest number of wins.
    If no new opponent is available, allows rematches, still prioritizing closest wins.

    Args:
        player1_id: The ID of the player needing an opponent.
        potential_opponents_ids: A list of IDs of available potential opponents.
        players_data: The main dictionary holding all player data (wins, played set).

    Returns:
        The ID of the best opponent found, or None if potential_opponents_ids is empty.
    """
    if not potential_opponents_ids:
        return None

    p1_wins = players_data[player1_id]["wins"]
    p1_played = players_data[player1_id]["played"]

    best_match_id = None
    best_match_score = float('inf') # Lower is better (win_difference)
    found_new_opponent = False

    # Sort potential opponents by win difference primarily
    sorted_opponents = sorted(
        potential_opponents_ids,
        key=lambda opp_id: abs(players_data[opp_id]["wins"] - p1_wins)
    )

    # --- Attempt 1: Find best NEW opponent ---
    for p2_id in sorted_opponents:
        if p2_id not in p1_played:
            # This is the best new opponent because the list is sorted by win difference
            best_match_id = p2_id
            found_new_opponent = True
            break # Found the best possible new opponent

    # --- Attempt 2: If no new opponent, find best REMATCH opponent ---
    if not found_new_opponent:
        # The best rematch opponent is simply the first one in the sorted list
        # as it has the minimum win difference.
        if sorted_opponents: # Ensure the list wasn't empty
             best_match_id = sorted_opponents[0]

    return best_match_id


def speed_chess_tournament_fixed_pairing(num_players=10, num_rounds=3, rated_percentage=0.8):
    """Simulates an interactive speed chess tournament with a robust pairing
    algorithm ensuring all players play each round (or one gets a bye if odd).
    Prioritizes pairing based on performance (wins) and avoiding rematches.

    Args:
        num_players (int): The number of players in the tournament.
        num_rounds (int): The number of rounds in the tournament.
        rated_percentage (float): Percentage of players with ratings (0.0 to 1.0).

    Returns:
        dict: A dictionary containing the final results of the tournament.
    """
    # --- Input Validation within function start (optional but good practice) ---
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

    players = {}
    for i in range(1, num_players + 1):
        rating = random.randint(1000, 2000) if random.random() <= rated_percentage else None
        players[i] = {"rating": rating, "wins": 0, "losses": 0, "draws": 0, "played": set()}

    tournament_history = defaultdict(list) # Store list of (p1, p2) pairs per round
    bye_player_id = None # Track player with bye in the current round

    print(f"\nStarting Fixed Pairing Speed Chess Tournament: {num_players} players, {num_rounds} rounds ({rated_percentage*100:.0f}% rated)")

    for round_num in range(1, num_rounds + 1):
        print(f"\n--- Round {round_num} Pairings ---")
        round_pairings_list = [] # List to store (p1, p2) tuples for this round
        paired_ids_this_round = set() # Keep track of who is paired
        bye_player_id = None # Reset bye player for the round

        # Get players available for pairing this round
        unpaired_players_ids = list(players.keys())
        random.shuffle(unpaired_players_ids) # Initial shuffle for tie-breaking randomness

        # Sort by wins (descending) to prioritize pairing top players
        unpaired_players_ids.sort(key=lambda pid: players[pid]["wins"], reverse=True)

        # Create a list to safely iterate while modifying
        players_to_pair = list(unpaired_players_ids)

        while len(players_to_pair) >= 2:
            # Select the highest priority player remaining
            p1_id = players_to_pair.pop(0)

            # Find potential opponents (those remaining in players_to_pair)
            potential_opponents = list(players_to_pair) # Make a copy

            if not potential_opponents:
                 players_to_pair.insert(0, p1_id) # Put player back if no opponents found
                 break

            # Find the best opponent using the helper function
            p2_id = find_best_opponent(p1_id, potential_opponents, players)

            if p2_id:
                # Pair found
                pair = tuple(sorted((p1_id, p2_id)))
                round_pairings_list.append(pair)
                players[p1_id]["played"].add(p2_id)
                players[p2_id]["played"].add(p1_id)
                paired_ids_this_round.add(p1_id)
                paired_ids_this_round.add(p2_id)
                players_to_pair.remove(p2_id)
            else:
                print(f"Warning: Could not find opponent for {p1_id} despite available players?")
                # If this happens, put p1 back in list to potentially get bye
                players_to_pair.insert(0, p1_id)


        # --- Check for the single unpaired player (bye) ---
        if len(players_to_pair) == 1:
             bye_player_id = players_to_pair[0]
             print(f"Player {bye_player_id} has a bye this round (odd number of players).")
             # Optionally add bye point: players[bye_player_id]["wins"] += 1
        elif len(players_to_pair) > 1:
             # This indicates a bug in the pairing logic if it happens
             print(f"ERROR: Pairing logic failed. Multiple players left unpaired: {players_to_pair}")


        tournament_history[round_num] = round_pairings_list # Store the actual pairs

        # --- Display Pairings ---
        print(f"Round {round_num} Actual Pairings:\n")
        displayed_matches = set() # Use set of sorted tuples to track displayed matches
        if not round_pairings_list:
             print("No matches played this round.")
        else:
            board_num = 0
            for p1, p2 in round_pairings_list:
                 board_num += 1 
                 rating_info_p1 = f"(Rated: {players[p1]['rating']})" if players[p1]['rating'] is not None else f"(Unrated, Wins: {players[p1]['wins']})"
                 rating_info_p2 = f"(Rated: {players[p2]['rating']})" if players[p2]['rating'] is not None else f"(Unrated, Wins: {players[p2]['wins']})"
                 print(f"Board {board_num}:  {p1} {rating_info_p1} vs {p2} {rating_info_p2}")
                 print("-------------------------------------------------------------------")
                 displayed_matches.add(tuple(sorted((p1, p2)))) # Add the canonical pair tuple

        # --- Get Round Results ---
        winners = []
        draws = []
        if displayed_matches: # Only ask for results if matches occurred
            while True: # Loop for results input validation
                winners_input = input(f"Enter the list of winners for Round {round_num} (comma-separated IDs, blank if none): ").strip()
                if winners_input:
                    try:
                        winners = [int(x.strip()) for x in winners_input.split(',') if x.strip()]
                        if not all(wid in players for wid in winners):
                            print("Invalid player ID entered in winners list. Try again.")
                            continue
                        if bye_player_id in winners:
                             print(f"Player {bye_player_id} had a bye and cannot be a winner. Try again.")
                             continue
                    except ValueError:
                        print("Invalid input for winners. Please enter comma-separated numbers. Try again.")
                        continue
                else:
                    winners = []

                draws_input = input(f"Enter drawn matches for Round {round_num} (pairs like '1-2,3-4', blank if none): ").strip()
                draws = []
                valid_draws = True
                if draws_input:
                    draw_pairs_str = draws_input.split(',')
                    for pair_str in draw_pairs_str:
                        try:
                            p1_str, p2_str = pair_str.strip().split('-')
                            p1, p2 = int(p1_str), int(p2_str)
                            draw_pair = tuple(sorted((p1, p2)))
                            if draw_pair not in displayed_matches:
                                print(f"Invalid draw pair: {p1}-{p2} was not a match this round. Try again.")
                                valid_draws = False
                                break
                            if p1 in winners or p2 in winners:
                                print(f"Invalid input: Player in draw pair {p1}-{p2} also listed as a winner. Try again.")
                                valid_draws = False
                                break
                            draws.append(draw_pair)
                        except ValueError:
                            print("Invalid draw format. Please use 'player1-player2'. Try again.")
                            valid_draws = False
                            break
                if not valid_draws:
                    continue # Restart results input if draws were invalid

                # Final validation: Ensure a match isn't both won and drawn
                all_players_in_results = set(winners)
                for p1d, p2d in draws:
                    all_players_in_results.add(p1d)
                    all_players_in_results.add(p2d)

                all_players_in_matches = set()
                for p1m, p2m in displayed_matches:
                    all_players_in_matches.add(p1m)
                    all_players_in_matches.add(p2m)

                if not all_players_in_results.issubset(all_players_in_matches):
                     missing = all_players_in_results - all_players_in_matches
                     print(f"Error: Player(s) {missing} reported in results but didn't play a match this round. Try again.")
                     continue

                # Check if all matches have a result (win or draw)
                matches_with_results = set(draws)
                for p1w in winners:
                    found_match = False
                    for p1m, p2m in displayed_matches:
                        if p1w == p1m or p1w == p2m:
                             matches_with_results.add(tuple(sorted((p1m,p2m))))
                             found_match = True
                             break
                    if not found_match:
                        # This check might be redundant due to earlier checks, but good safety
                        print(f"Error: Winner {p1w} doesn't correspond to a match played. Try again.")
                        valid_draws = False # Use flag to indicate error
                        break
                if not valid_draws: continue # Restart if winner error found

                if len(matches_with_results) != len(displayed_matches):
                     unaccounted_matches = displayed_matches - matches_with_results
                     print(f"Warning: Not all matches have results. Matches unaccounted for: {unaccounted_matches}. Please verify input.")
                     # Decide whether to proceed or force user correction
                     # For now, let's proceed but warn. To force correction, add 'continue' here.

                break # Results seem valid enough to proceed


        # --- Update Player Records based on Results ---
        processed_matches = set()

        # Process winners
        for p1_wins_id in winners:
            opponent_found = False
            for p1_match, p2_match in displayed_matches:
                 match_pair = tuple(sorted((p1_match, p2_match)))
                 if match_pair in processed_matches or match_pair in draws:
                     continue # Already processed or is a draw

                 p1_actual, p2_actual = match_pair

                 if p1_wins_id == p1_actual:
                     players[p1_actual]["wins"] += 1
                     players[p2_actual]["losses"] += 1
                     processed_matches.add(match_pair)
                     opponent_found = True
                     break
                 elif p1_wins_id == p2_actual:
                     players[p2_actual]["wins"] += 1
                     players[p1_actual]["losses"] += 1
                     processed_matches.add(match_pair)
                     opponent_found = True
                     break

        # Process draws
        for p1_draw, p2_draw in draws:
             match_pair = tuple(sorted((p1_draw, p2_draw)))
             if match_pair not in processed_matches:
                 players[p1_draw]["draws"] += 1
                 players[p2_draw]["draws"] += 1
                 processed_matches.add(match_pair)

        # Check for matches without results (should have been caught by validation, but as fallback)
        for p1_match, p2_match in displayed_matches:
            match_pair = tuple(sorted((p1_match, p2_match)))
            if match_pair not in processed_matches:
                 print(f"Warning: Match {p1_match} vs {p2_match} result was not processed. Check input.")


        print("\n--- End of Round", round_num, "---")

    print("\n--- Tournament Finished ---")
    print("\nFinal Player Records:")
    sorted_player_ids = sorted(players.keys(), key=lambda pid: players[pid]["wins"], reverse=True)
    for player_id in sorted_player_ids:
        data = players[player_id]
        rating_info = f"(Rated: {data['rating']})" if data['rating'] is not None else "(Unrated)"
        # Calculate points (optional): wins=1, draw=0.5
        points = data['wins'] + 0.5 * data['draws']
        print(f"Player {player_id} {rating_info}: Points={points} (W:{data['wins']}, L:{data['losses']}, D:{data['draws']})")

    return {"players": players, "history": dict(tournament_history)}


# ==================================================
# Main execution block - Handles User Input
# ==================================================
if __name__ == "__main__":
    print("--- Chess Tournament Setup ---")

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

    # Call the main tournament function with user-provided values
    tournament_results = speed_chess_tournament_fixed_pairing(
        num_players=num_players,
        num_rounds=num_rounds,
        rated_percentage=rated_percentage
    )

    if tournament_results:
        print("\n--- Tournament Simulation Complete ---")
    else:
        print("\n--- Tournament Simulation Failed (Input Error?) ---")
