import pygame

import config as _cfg
from simulation.person import Status
from simulation.ui_theme import (
    BG_HEADER, BG_PANEL, BG_CHART,
    COLOR_BORDER, COLOR_GRID,
    COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_S, COLOR_I, COLOR_R,
    COLOR_ACCENT, COLOR_SEPARATOR,
)

_SERIES = [
    (Status.S, COLOR_S, "Podatni (S)"),
    (Status.I, COLOR_I, "Zakażeni (I)"),
    (Status.R, COLOR_R, "Ozdrowiali (R)"),
]


def draw_header(surface: pygame.Surface, step: int, scenario_name: str,
                font: pygame.font.Font, font_small: pygame.font.Font, paused: bool):
    w = surface.get_width()
    header_rect = pygame.Rect(0, 0, w, _cfg.HEADER_HEIGHT)
    pygame.draw.rect(surface, BG_HEADER, header_rect)
    pygame.draw.line(surface, COLOR_BORDER, (0, _cfg.HEADER_HEIGHT - 1), (w, _cfg.HEADER_HEIGHT - 1))

    cy = _cfg.HEADER_HEIGHT // 2

    # Left: app title
    title = font_small.render("SYMULACJA EPIDEMII", True, COLOR_TEXT_DIM)
    surface.blit(title, (16, cy - title.get_height() // 2))

    # Center: scenario badge
    badge_label = scenario_name.upper().replace("_", " ")
    badge_surf = font_small.render(badge_label, True, COLOR_TEXT)
    bw = badge_surf.get_width() + 20
    bh = badge_surf.get_height() + 8
    badge_rect = pygame.Rect(w // 2 - bw // 2, cy - bh // 2, bw, bh)
    pygame.draw.rect(surface, COLOR_ACCENT, badge_rect, border_radius=10)
    surface.blit(badge_surf, (badge_rect.x + 10, badge_rect.y + 4))

    # Right: step counter + pause indicator
    right_parts = [f"krok: {step:,}"]
    if paused:
        right_parts.insert(0, "⏸ PAUZA  ")
    right_text = "".join(right_parts)
    right_surf = font_small.render(right_text, True, COLOR_TEXT_DIM)
    surface.blit(right_surf, (w - right_surf.get_width() - 16, cy - right_surf.get_height() // 2))


def draw_stats_panel(surface: pygame.Surface, model,
                     font: pygame.font.Font, font_small: pygame.font.Font,
                     rect: pygame.Rect):
    pygame.draw.rect(surface, BG_PANEL, rect)
    pygame.draw.line(surface, COLOR_SEPARATOR, rect.topleft, rect.bottomleft)

    population = len(model.people)
    row_h = rect.height // 3
    bar_w = rect.width - 28
    bar_h = 5

    for i, (status, color, label) in enumerate(_SERIES):
        count = model.count_status(status)
        fraction = count / population if population > 0 else 0
        ry = rect.y + i * row_h

        # Label + count
        label_surf = font_small.render(label, True, COLOR_TEXT_DIM)
        count_surf = font.render(str(count), True, color)
        surface.blit(label_surf, (rect.x + 14, ry + 8))
        surface.blit(count_surf, (rect.x + 14, ry + 24))

        # Progress bar
        bx = rect.x + 14
        by = ry + row_h - 12
        pygame.draw.rect(surface, COLOR_GRID, (bx, by, bar_w, bar_h), border_radius=3)
        if fraction > 0:
            pygame.draw.rect(surface, color, (bx, by, int(bar_w * fraction), bar_h), border_radius=3)

        # Percentage
        pct_surf = font_small.render(f"{fraction * 100:.1f}%", True, COLOR_TEXT_DIM)
        surface.blit(pct_surf, (rect.right - pct_surf.get_width() - 8, ry + 24))

        # Colored dot next to label
        pygame.draw.circle(surface, color, (rect.x + 6, ry + 8 + label_surf.get_height() // 2), 4)

        # Row separator
        if i < 2:
            pygame.draw.line(surface, COLOR_SEPARATOR,
                             (rect.x + 1, ry + row_h),
                             (rect.right, ry + row_h))


def draw_live_chart(surface: pygame.Surface, history: dict,
                    rect: pygame.Rect, font_tiny: pygame.font.Font):
    pygame.draw.rect(surface, BG_CHART, rect, border_radius=4)
    pygame.draw.rect(surface, COLOR_BORDER, rect, 1, border_radius=4)

    pad = 8
    inner = pygame.Rect(rect.x + pad, rect.y + pad, rect.width - 2 * pad, rect.height - 2 * pad)

    population = _cfg.POPULATION_SIZE
    n_points = len(history["S"])

    # Grid (5 horizontal lines)
    for k in range(1, 5):
        gy = inner.bottom - int(inner.height * k / 4)
        pygame.draw.line(surface, COLOR_GRID, (inner.left, gy), (inner.right, gy))
        label_val = int(population * k / 4)
        lbl = font_tiny.render(str(label_val), True, COLOR_TEXT_DIM)
        surface.blit(lbl, (inner.left - lbl.get_width() - 2, gy - lbl.get_height() // 2))

    if n_points < 2:
        msg = font_tiny.render("brak danych...", True, COLOR_TEXT_DIM)
        surface.blit(msg, (inner.centerx - msg.get_width() // 2, inner.centery - msg.get_height() // 2))
    else:
        # Subsample to at most inner.width points
        step = max(1, n_points // inner.width)

        for status, color, _ in _SERIES:
            values = history[status][::step]
            m = len(values)
            points = []
            for j, v in enumerate(values):
                px = inner.left + int(j * (inner.width - 1) / max(m - 1, 1))
                py = inner.bottom - int(v * inner.height / population)
                py = max(inner.top, min(inner.bottom, py))
                points.append((px, py))
            if len(points) >= 2:
                pygame.draw.aalines(surface, color, False, points)

    # Legend (top-right corner inside chart)
    legend_x = rect.right - 4
    legend_y = rect.top + 6
    for status, color, short_label in _SERIES:
        short = short_label.split()[0]  # "Podatni", "Zakażeni", "Ozdrowiali"
        lbl = font_tiny.render(short, True, color)
        legend_x -= lbl.get_width() + 14
        pygame.draw.circle(surface, color, (legend_x - 4, legend_y + lbl.get_height() // 2), 3)
        surface.blit(lbl, (legend_x, legend_y))


def draw_section_label(surface: pygame.Surface, text: str,
                       x: int, y: int, font: pygame.font.Font):
    lbl = font.render(text, True, COLOR_TEXT_DIM)
    surface.blit(lbl, (x, y))


# Legacy — kept for compatibility; not used in new UI
def draw_stats(screen, model, font):
    susceptible = model.count_status(Status.S)
    infected = model.count_status(Status.I)
    recovered = model.count_status(Status.R)
    text = f"S: {susceptible}   I: {infected}   R: {recovered}"
    surface = font.render(text, True, (0, 0, 0))
    screen.blit(surface, _cfg.STATS_POSITION)
