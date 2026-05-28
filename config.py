from pathlib import Path

import yaml

_ROOT = Path(__file__).parent
_SELECTOR_PATH = _ROOT / "config.yaml"
_BASE_CONFIG_PATH = _ROOT / "config" / "base.yaml"
_SCENARIOS_DIR = _ROOT / "config" / "scenarios"


def _build_config(selected: str) -> dict:
    config = yaml.safe_load(_BASE_CONFIG_PATH.read_text(encoding="utf-8"))

    scenario_path = _SCENARIOS_DIR / f"{selected}.yaml"
    if not scenario_path.exists():
        available = sorted(p.stem for p in _SCENARIOS_DIR.glob("*.yaml"))
        raise ValueError(
            f"Nieznany scenariusz: '{selected}'. Dostępne: {', '.join(available)}"
        )

    override = yaml.safe_load(scenario_path.read_text(encoding="utf-8")) or {}
    config.update(override)

    config["SCENARIO_NAME"] = selected
    config["GIF_PATH"] = str(Path(config["RESULTS_DIR"]) / f"epidemia_{selected}.gif")
    config["PLOT_PATH"] = str(Path(config["RESULTS_DIR"]) / f"wykres_{selected}.png")

    return config


def load_config() -> dict:
    selected = yaml.safe_load(_SELECTOR_PATH.read_text(encoding="utf-8"))["selected_scenario"]
    return _build_config(selected)


def reload_for_scenario(name: str):
    """Reload config globals for a different scenario (in-game switching)."""
    new_config = _build_config(name)
    import sys
    this_module = sys.modules[__name__]
    for key, value in new_config.items():
        setattr(this_module, key, value)


_config = load_config()

globals().update(_config)
