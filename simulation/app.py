import ctypes
import sys
from pathlib import Path

import pygame

# Tell Windows to render at native resolution instead of scaling the window.
# Without this, Windows DPI scaling makes everything blurry on high-DPI screens.
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per-monitor DPI aware v2
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()       # fallback (Windows 8.1+)

import config as _cfg
from config import WIDTH, HEIGHT, FPS, PANEL_WIDTH, HEADER_HEIGHT

from simulation.model import SimulationModel
from simulation.visualization import (
    draw_header, draw_stats_panel, draw_live_chart, draw_section_label,
)
from simulation.plots import show_plot
from simulation.recorder import GifRecorder
from simulation.scenarios.registry import get_scenario
from simulation.ui.controls import Button
from simulation.ui_theme import (
    BG_WINDOW, BG_SIM, BG_PANEL,
    COLOR_BORDER, COLOR_SEPARATOR,
)

_SCENARIOS_DIR = Path(__file__).parents[1] / "config" / "scenarios"

CHART_UPDATE_INTERVAL = 6


def _available_scenarios() -> list[str]:
    return sorted(p.stem for p in _SCENARIOS_DIR.glob("*.yaml"))


def _make_simulation(name: str):
    _cfg.reload_for_scenario(name)
    scenario = get_scenario(name)
    model = SimulationModel(scenario)
    recorder = GifRecorder() if _cfg.SAVE_GIF else None
    return scenario, model, recorder


def run_simulation():
    pygame.init()

    win_w = WIDTH + PANEL_WIDTH
    win_h = HEIGHT + HEADER_HEIGHT
    window = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("Symulacja epidemii SIR")

    clock = pygame.time.Clock()
    font       = pygame.font.SysFont(None, 26)
    font_small = pygame.font.SysFont(None, 19)
    font_tiny  = pygame.font.SysFont(None, 15)

    available = _available_scenarios()
    current_name = _cfg.SCENARIO_NAME

    # ── Sim subsurface ──────────────────────────────────────────────────
    sim_surface = window.subsurface(pygame.Rect(0, HEADER_HEIGHT, WIDTH, HEIGHT))

    # ── Panel layout ────────────────────────────────────────────────────
    px = WIDTH + 10
    pw = PANEL_WIDTH - 20
    py = HEADER_HEIGHT

    stats_rect  = pygame.Rect(WIDTH, py, PANEL_WIDTH, 110)
    chart_top   = py + 110 + 10
    chart_h     = 240
    chart_rect  = pygame.Rect(px, chart_top, pw, chart_h)

    # Persistent chart surface — avoids flicker caused by BG_PANEL fill
    chart_surf = pygame.Surface((pw, chart_h))

    # Scenario buttons (2 columns, dynamic)
    btn_section_y = chart_top + chart_h + 14
    btn_w = (pw - 10) // 2
    scenario_buttons: list[Button] = []
    for i, name in enumerate(available):
        col = i % 2
        row = i // 2
        bx = px + col * (btn_w + 10)
        by = btn_section_y + 16 + row * 32
        scenario_buttons.append(Button(
            (bx, by, btn_w, 26),
            name.replace("_", " "),
            active=(name == current_name),
            font_size=14,
        ))

    n_rows = (len(available) + 1) // 2
    ctrl_y = btn_section_y + 16 + n_rows * 32 + 12

    btn_pause = Button((px, ctrl_y, 90, 28), "Pauza", font_size=15)
    btn_reset = Button((px + 100, ctrl_y, 80, 28), "Reset", font_size=15)

    speed_labels = ["×1", "×2", "×4"]
    speed_values = [1,    2,    4]
    speed_btns = [
        Button((px + j * 46, ctrl_y + 52, 40, 26), lbl, active=(j == 0), font_size=14)
        for j, lbl in enumerate(speed_labels)
    ]

    # ── Simulation state ─────────────────────────────────────────────────
    scenario, model, recorder = _make_simulation(current_name)
    paused = False
    speed  = 1
    step   = 0
    chart_tick = 0
    chart_needs_reset = True
    epidemic_ended = False

    def reset(name: str):
        nonlocal scenario, model, recorder, current_name
        nonlocal paused, speed, step, chart_tick, chart_needs_reset, epidemic_ended
        paused = False
        speed  = 1
        step   = 0
        chart_tick = 0
        chart_needs_reset = True
        epidemic_ended = False
        btn_pause.label = "Pauza"
        for b in speed_btns:
            b.active = False
        speed_btns[0].active = True
        for b in scenario_buttons:
            b.active = (b.label == name.replace("_", " "))
        scenario, model, recorder = _make_simulation(name)
        current_name = name

    running = True

    while running:
        # ── Events ──────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(scenario_buttons):
                    if btn.is_clicked(event):
                        reset(available[i])

                if btn_pause.is_clicked(event):
                    paused = not paused
                    btn_pause.label = "Wznów" if paused else "Pauza"

                if btn_reset.is_clicked(event):
                    reset(current_name)

                for i, btn in enumerate(speed_btns):
                    if btn.is_clicked(event):
                        for b in speed_btns:
                            b.active = False
                        btn.active = True
                        speed = speed_values[i]

        # ── Update ──────────────────────────────────────────────────────
        if not paused:
            for _ in range(speed):
                model.update()
                step += 1

            # Detect epidemic end: no infected left after simulation started
            if not epidemic_ended and step > 10 and model.count_status("I") == 0:
                epidemic_ended = True
                show_plot(model.history)
                chart_needs_reset = True

        # ── Render ──────────────────────────────────────────────────────
        window.fill(BG_WINDOW)

        # Simulation area
        sim_surface.fill(BG_SIM)
        scenario.draw_environment(sim_surface)
        for person in model.people:
            person.draw(sim_surface)

        if epidemic_ended:
            msg = font_small.render("Epidemia wygasła — wykres zapisany", True, (55, 205, 115))
            sim_surface.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT - 30))

        # Panel background + vertical separator
        pygame.draw.rect(window, BG_PANEL, (WIDTH, HEADER_HEIGHT, PANEL_WIDTH, HEIGHT))
        pygame.draw.line(window, COLOR_BORDER,
                         (WIDTH, HEADER_HEIGHT), (WIDTH, HEADER_HEIGHT + HEIGHT))

        # Stats
        draw_stats_panel(window, model, font, font_small, stats_rect)
        pygame.draw.line(window, COLOR_SEPARATOR,
                         (WIDTH + 1, py + 110), (WIDTH + PANEL_WIDTH, py + 110))

        # Live chart — update offscreen surface, then blit (no flicker)
        chart_tick += 1
        if chart_needs_reset or chart_tick % CHART_UPDATE_INTERVAL == 0:
            local_rect = pygame.Rect(0, 0, pw, chart_h)
            draw_live_chart(chart_surf, model.history, local_rect, font_tiny)
            chart_needs_reset = False
        window.blit(chart_surf, (chart_rect.x, chart_rect.y))

        pygame.draw.line(window, COLOR_SEPARATOR,
                         (WIDTH + 1, chart_top + chart_h + 8),
                         (WIDTH + PANEL_WIDTH, chart_top + chart_h + 8))

        # Scenario selector
        draw_section_label(window, "SCENARIUSZ", px, btn_section_y, font_tiny)
        for btn in scenario_buttons:
            btn.draw(window)

        pygame.draw.line(window, COLOR_SEPARATOR,
                         (WIDTH + 1, ctrl_y - 8), (WIDTH + PANEL_WIDTH, ctrl_y - 8))

        # Controls
        draw_section_label(window, "KONTROLKI", px, ctrl_y - 8 + 2, font_tiny)
        btn_pause.draw(window)
        btn_reset.draw(window)
        spd_lbl = font_tiny.render("prędkość:", True, (80, 92, 130))
        window.blit(spd_lbl, (px, ctrl_y + 38))
        for btn in speed_btns:
            btn.draw(window)

        # Header (on top of everything)
        draw_header(window, step, current_name, font, font_small, paused)

        if recorder:
            recorder.capture(sim_surface)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

    if recorder:
        recorder.save()

    show_plot(model.history)
