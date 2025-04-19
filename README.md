# Interactive Chess Tournament Pairing Script

This Python script helps manage a multi-round chess tournament interactively. It sets up the tournament based on user input, generates pairings each round using a performance-based algorithm, and requires the user to input the results (winners and draws) after each round to update standings.

## Features

* **Interactive Setup:** Prompts the user for key tournament parameters:
    * Total number of players (must be >= 2).
    * Number of rounds (must be >= 1).
    * Target percentage of players to be assigned ratings (0.0 to 1.0).
* **Rated & Unrated Players:**
    * Supports a mix of players with assigned ratings and unrated players.
    * Rated players are assigned a random initial rating (default: 1000-2000).
    * The assignment is non-deterministic; each player has the specified percentage chance of receiving a rating.
* **Robust Pairing Algorithm (`find_best_opponent`):**
    * Pairs players primarily based on their current win count (players with similar scores play each other).
    * Prioritizes pairing opponents who haven't played before in the tournament.
    * Allows rematches if necessary to ensure all players are paired in a round.
    * Correctly handles byes for an odd number of players (one player sits out).
* **Interactive Round Management:**
    * Displays pairings clearly each round, showing player IDs and rating/win information.
    * Prompts the user to enter the list of winning player IDs for the round.
    * Prompts the user to enter any drawn matches using a simple pair format (e.g., `1-2,3-4`).
    * Includes input validation to help catch errors in result entry.
    * Updates player scores (wins, losses, draws) based on the entered results.
* **Final Standings:** Outputs final tournament standings sorted by points (Win=1, Draw=0.5) at the conclusion of all rounds.

## Requirements

* Python 3.x
* Standard Python libraries: `random`, `collections` (no external packages needed).

## Usage

1.  Save the code as a Python file (e.g., `interactive_tournament.py`).
2.  Run the script from your terminal:
    ```bash
    python interactive_tournament.py
    ```
3.  Follow the prompts to enter the initial setup information:
    * Total number of players.
    * Number of rounds.
    * Percentage of rated players (e.g., `0.8` for 80%).
4.  **For each round:**
    * The script will display the generated pairings.
    * You will be prompted to enter the **list of winners** for the round (comma-separated player IDs). Press Enter if there were no decisive games.
    * You will be prompted to enter any **drawn matches** using the format `player1ID-player2ID`, separated by commas (e.g., `3-5, 10-2`). Press Enter if there were no draws.
    * The script validates the input and updates the scores.
5.  After the final round is completed and results are entered, the final standings will be displayed.

## Customization

You can modify the script's behavior by adjusting:

* **Initial Rating Range**: Modify the `random.randint(1000, 2000)` call in the `speed_chess_tournament_fixed_pairing` function's player initialization loop to change the range for assigned ratings.
* **Bye Points**: Currently, players receiving a bye do not automatically get points. You can uncomment or add logic (e.g., `players[bye_player_id]["wins"] += 1`) in the "Check for the single unpaired player (bye)" section if you want byes to award points.
* **Point System**: The final display uses 1 point for a win and 0.5 for a draw. This calculation within the final print loop can be adjusted if needed.

------------------------------

# Chess Tournament Simulator

This Python script simulates a multi-round chess tournament using a pairing system that prioritizes matching players with similar win records while minimizing rematches. It handles both rated and unrated players and automatically simulates match outcomes based on relative ratings after an initial interactive setup.

## Features

* **Interactive Setup:** Prompts the user for key tournament parameters:
    * Total number of players (must be >= 2).
    * Number of rounds (must be >= 1).
    * Target percentage of players to be assigned ratings (0.0 to 1.0).
* **Rated & Unrated Players:**
    * Supports a mix of players with assigned ratings and unrated players.
    * Rated players are assigned a random initial rating (default: 1000-2000).
    * The *actual* number of rated players assigned may vary slightly due to the probabilistic assignment (`random.random() < rated_percentage`).
* **Robust Pairing Algorithm (`find_best_opponent`):**
    * Pairs players primarily based on their current win count (players with similar scores play each other).
    * Prioritizes pairing opponents who haven't played before in the tournament.
    * Allows rematches if necessary to ensure all players are paired in a round.
    * Correctly handles byes for an odd number of players (one player sits out).
* **Non-Interactive Round Simulation:**
    * After setup, the script runs automatically without needing input for each round's results.
    * Match outcomes (Win/Loss/Draw) are determined automatically using the `simulate_match_result` function.
    * Simulation uses a probabilistic model based on player ratings (assigns a default rating to unrated players for the simulation).
* **Clear Console Output:**
    * Shows initialization details (number of players rated).
    * For each round: displays pairings and the simulated results.
    * Displays final tournament standings sorted by points (Win=1, Draw=0.5).

## Requirements

* Python 3.x
* Standard Python libraries: `random`, `collections` (no external packages needed).

## Usage

1.  Save the code as a Python file (e.g., `tournament_simulator.py`).
2.  Run the script from your terminal:
    ```bash
    python tournament_simulator.py
    ```
3.  Follow the prompts to enter the required setup information:
    * Total number of players.
    * Number of rounds.
    * Percentage of rated players (e.g., `0.8` for 80%).
4.  The script will then print the initialization details and simulate each round, showing pairings and simulated results.
5.  The final standings, sorted by points, will be displayed at the end of the simulation.

## Simulation Logic

Match results in each round are simulated automatically by the `simulate_match_result` function:

1.  **Rating Assignment:** For simulation purposes, any unrated player is temporarily assigned a default rating (`DEFAULT_UNRATED_SIM_RATING`, currently 1400).
2.  **Probability Calculation:** The probability of Player 1 winning, Player 2 winning, or a draw is calculated based on the rating difference between the two players.
3.  **Outcome Determination:** `random.choices` is used to select the outcome (Player 1 wins, Player 2 wins, or Draw) based on the calculated probabilities. A larger rating difference gives the higher-rated player a higher chance of winning, but upsets are possible due to the element of randomness.

## Customization

You can modify the script's behavior by adjusting:

* **`DEFAULT_UNRATED_SIM_RATING`**: Change the assumed strength of unrated players during simulation (defined near the top).
* **Initial Rating Range**: Modify the `random.randint(1000, 2000)` call in the player initialization loop to change the range for assigned ratings.
* **Simulation Probabilities**: Adjust the rating difference thresholds and corresponding win/loss/draw probabilities within the `simulate_match_result` function to fine-tune the simulation realism.
* **Bye Points**: Currently, players receiving a bye do not automatically get points. You can uncomment or add logic (e.g., `players[bye_player_id]["wins"] += 1`) in the "Check for Bye" section if desired.
