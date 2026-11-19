"""Main GUI application for Griductive Solver (Member 5).
Includes:
- Level Selector (6 test cases from data/)
- Restart control
- Interactive Clue Highlight on click (uses RegionHelper)
- Manual play mode with NOT_PROVABLE / CONTRADICTED feedback
- Auto-solve with step-by-step animation
"""
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Source.engine.puzzle_io import load_puzzle
from Source.engine.engine import GameEngine
from Source.engine.region_helper import RegionHelper

class GriductiveGUI:
    """GUI Window for Griductive game.
    TV5 can implement this using Tkinter (standard library), Pygame, or PyQt.
    """
    def __init__(self, puzzle_path: str = "data/sample_3x3.json"):
        self.puzzle_path = puzzle_path
        self.engine = None
        self.selected_clue_region = []
        self._init_game()

    def _init_game(self):
        """Loads puzzle and initializes GameEngine."""
        puzzle_data = load_puzzle(self.puzzle_path)
        self.engine = GameEngine(puzzle_data)

    def on_cell_clicked(self, cell_id: str, verdict: str):
        """Called when user submits a verdict for a cell in manual play mode."""
        result = self.engine.submit_verdict(cell_id, verdict)
        # TODO [TV5]:
        # - If result.is_valid: update card display, show clue, play success effect.
        # - Else: show popup / status message with result.status_code (NOT_PROVABLE or CONTRADICTED).
        print(f"Verdict {verdict} for {cell_id}: {result.status_code} - {result.message}")

    def on_clue_selected(self, clue_dict: dict):
        """Called when user clicks on a revealed clue to highlight its region."""
        region_dict = clue_dict.get("params", {}).get("region")
        if region_dict:
            self.selected_clue_region = RegionHelper.resolve_region(region_dict, self.engine.size)
            # TODO [TV5]: Visually highlight cells in self.selected_clue_region on the grid
            print(f"Highlighting cells in region: {self.selected_clue_region}")

    def on_auto_solve_clicked(self, agent):
        """Called when user clicks 'Auto Solve'.
        Must animate step-by-step with a short delay (e.g. 500ms between reveal waves).
        """
        # TODO [TV5]:
        # Loop over agent.solve_step(self.engine.get_public_state())
        # Animate each flip on the GUI with timer delay
        pass

    def on_restart_clicked(self):
        """Resets current game board to initial revealed state."""
        self.engine.restart()
        # TODO [TV5]: Redraw UI

def start_app():
    print("Launching Griductive GUI template...")
    # TODO [TV5]: Initialize window and run main event loop (e.g. root.mainloop())
    gui = GriductiveGUI()
    print("GUI template initialized with sample_3x3 puzzle successfully.")

if __name__ == '__main__':
    start_app()
