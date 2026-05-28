import pygame

from simulation.ui_theme import (
    COLOR_BTN,
    COLOR_BTN_HOVER,
    COLOR_BTN_ACTIVE,
    COLOR_BTN_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
)

_font_cache: dict = {}


def _get_font(size: int) -> pygame.font.Font:
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont(None, size)
    return _font_cache[size]


class Button:
    def __init__(self, rect, label: str, active: bool = False, font_size: int = 15):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.active = active
        self.font_size = font_size

    def draw(self, surface: pygame.Surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())

        if self.active:
            bg = COLOR_BTN_ACTIVE
            text_color = COLOR_TEXT
        elif hovered:
            bg = COLOR_BTN_HOVER
            text_color = COLOR_TEXT
        else:
            bg = COLOR_BTN
            text_color = COLOR_TEXT_DIM

        pygame.draw.rect(surface, bg, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BTN_BORDER, self.rect, 1, border_radius=6)

        font = _get_font(self.font_size)
        text_surf = font.render(self.label, True, text_color)
        tx = self.rect.centerx - text_surf.get_width() // 2
        ty = self.rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (tx, ty))

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )
