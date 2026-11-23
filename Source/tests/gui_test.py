import os, sys
sys.path.insert(0, ".")

def main():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    import pygame
    from Source.gui.app import GriductiveApp

    app = GriductiveApp()
    app.htp_popup.is_open = False
    print("levels:", [os.path.basename(p) for p in app.puzzle_files])

    def shot(name):
        app.draw()
        pygame.image.save(app.screen, f"shots/{name}.png")

    os.makedirs("shots", exist_ok=True)
    app.load_level(0)
    shot("01_start")

    # click lên ô A1 (đã lộ) rồi ô B1 (úp)
    app.select_cell("A2")
    shot("02_select_revealed")

    app.select_cell("C3")
    app.call_verdict("CRIMINAL")
    print("status:", app.status_bar.message)
    shot("03_reject")

    app.do_hint()
    print("hint:", app.status_bar.message)
    shot("04_hint")

    for _ in range(3):
        app.do_step()
    print("step:", app.status_bar.message)
    shot("05_steps")

    while not app.session.terminal:
        app.do_step()
    print("end:", app.status_bar.message)
    shot("06_end")

    # 5x5 và puzzle sai
    for i, p in enumerate(app.puzzle_files):
        if "layout" in p:
            app.load_level(i)
            app.select_cell("B2")
            shot("07_layout5x5")
        if "sample_3x3" in p:
            app.load_level(i)
            for _ in range(12):
                app.do_step()
                if app.session.terminal:
                    break
            print("sample_3x3 ->", app.session.terminal, "|", app.status_bar.message)
            shot("08_sample_invalid")

if __name__ == "__main__":
    main()