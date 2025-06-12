# Python-Poker

A graphical implementation of Texas Hold'em Poker using Python and Pygame.

## Features

- **Texas Hold'em Poker game rules:** Play with up to 6 players (1 human, 5 computer bots).
- **Pygame interface:** Interactive table, player areas, card graphics, and chips.
- **Bot opponents:** Computer players with simple logic for betting, calling, folding, and raising.
- **Equity calculator:** In-game equity estimation for your hand on request.
- **Showdown:** Automatic hand ranking and winner determination, with hand breakdowns.
- **User interface:** Buttons for Fold, Check/Call, Bet/Raise, All-in, and Equity. Text input for custom raise amounts.
- **Game flow:** Blinds, betting rounds (pre-flop, flop, turn, river), and automatic game-over handling.


## Getting Started

### Requirements

- Python 3.7 or higher
- [Pygame](https://www.pygame.org/)

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/anshulboreda/Python-Poker.git
   cd Python-Poker
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Game

```bash
python deepseek_python_20250602_dd902d.py
```

### Controls

- The human player is always "You" at the bottom of the table.
- Use your mouse to select actions (Fold, Check/Call, Bet/Raise, All-in, Equity).
- When raising, enter a numeric amount in the text box and press Enter.
- Press `ESC` during Game Over to exit.

## File Structure

- `deepseek_python_20250602_dd902d.py` — Main game file containing all logic and graphical code.

## Notes

- The bot logic is intentionally simple and can be improved for stronger AI.
- The game supports a single human player against up to 5 computer bots.
- All cards and chips are drawn directly using Pygame—no external images required.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- Developed using [Pygame](https://www.pygame.org/).
- Poker logic inspired by standard Texas Hold'em rules.
