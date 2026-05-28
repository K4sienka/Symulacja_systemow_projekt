# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Symulacja rozprzestrzeniania się chorób w populacji** - An agent-based epidemiological simulation modeling disease spread in a population using the SIR (Susceptible-Infected-Recovered) model. This is an academic project for the "Modeling and Simulation of Systems" course.

- **Language**: Python 3
- **Main Technologies**: pygame (visualization), numpy, matplotlib (plotting), PyYAML (config)
- **Entry Point**: `python main.py`

## Quick Start

```bash
# Setup environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run simulation
python main.py
```

The simulation runs interactively with real-time visualization. Close the pygame window to end the simulation and see the matplotlib plot of SIR curves over time. Results (GIF and PNG) are saved to the `results/` directory.

## Architecture

### Core Components

**Simulation Model** (`simulation/model.py`)
- Manages population of `Person` agents, each with SIR status (S/I/R)
- Core infection spread: infected individuals within `INFECTION_RADIUS` can infect susceptible individuals with `INFECTION_PROBABILITY`
- Tracks `infected_time` for each infected person; transitions to recovered after `RECOVERY_TIME` frames
- Records `history` dict tracking counts of S/I/R at each timestep

**Person Agent** (`simulation/person.py`)
- Represents individual with position (x, y), velocity (vx, vy)
- Status: "S" (susceptible), "I" (infected), "R" (recovered)
- Bounces off screen edges
- Rendered as colored circles: blue (S), red (I), green (R)
- Scenario-specific attributes: `is_quarantined`, `target_x`/`target_y` (shop targeting), `shop_timer`/`shop_cooldown`

**Application Loop** (`simulation/app.py`)
- pygame event loop and rendering orchestration
- Each frame: scenario setup → movement → infection spread → recovery → visualization → optional GIF recording
- Post-simulation: saves GIF and displays matplotlib plot

### Scenario Plugin System

The simulation supports multiple scenarios via a plugin interface. Each scenario is a class implementing:

- `before_update(model)`: Called before movement each frame (used for quarantine logic, shop mechanics)
- `can_move(person)`: Returns whether person can move this frame
- `can_infect(infected_person)`: Returns whether infected person can transmit
- `get_infection_radius(infected, susceptible)`: Distance-based transmission parameter
- `get_infection_probability(infected, susceptible)`: Probability of transmission on contact
- `draw_environment(screen)`: Render scenario-specific visuals (e.g., shop location)

All scenarios inherit from **`BaseScenario`** (`simulation/scenarios/base_scenario.py`) which provides default no-op/passthrough implementations of the full interface. Subclasses override only what they need.

**Available Scenarios**:

1. **BasicScenario** (`simulation/scenarios/basic.py`): Pure SIR — inherits all defaults from `BaseScenario`, no overrides.
2. **QuarantineScenario** (`simulation/scenarios/quarantine.py`): Infected individuals automatically enter quarantine after `QUARANTINE_AFTER` frames, preventing both movement and transmission.
3. **ShopScenario** (`simulation/scenarios/shop.py`): Introduces a meeting point (tan circle). A subset of the population (`SHOP_VISITOR_SHARE`) can visit; higher infection rates inside (`SHOP_INFECTION_RADIUS`, `SHOP_INFECTION_PROBABILITY`). Capacity-limited with cooldowns. Uses `initialize(model)` to assign shop-visitor flags.
4. **CommunitiesScenario** (`simulation/scenarios/communities.py`): Divides population into `NUM_COMMUNITIES` groups with evenly-distributed center points. People are pulled back toward their community center (`COMMUNITY_RETURN_FORCE`). Within-community infection radius (`WITHIN_INFECTION_RADIUS`) is higher than between-community (`BETWEEN_INFECTION_RADIUS`).
5. **MobilityRestrictionsScenario** (`simulation/scenarios/mobility_restrictions.py`): When infected fraction exceeds `RESTRICTION_THRESHOLD`, all movement speeds are clamped to `RESTRICTED_SPEED`. Restrictions lift when infected fraction drops below `RESTRICTION_RELEASE_THRESHOLD`. Active restrictions shown as a red screen border.

Scenarios are registered in `simulation/scenarios/registry.py` and selected via `config.yaml`.

### Configuration System

Configuration is two-tiered:

- **`config.yaml`** (root) — only contains `selected_scenario: <name>`
- **`config/base.yaml`** — all shared parameters (display, population, infection, output, UI constants)
- **`config/scenarios/<name>.yaml`** — per-scenario overrides; only values that differ from base need to be listed

`config.py` loads base, then merges the selected scenario file on top, then exposes everything as module-level globals (`from config import WIDTH, HEIGHT, ...`). Adding a new scenario = add a `config/scenarios/<name>.yaml` file.

**Available scenarios**: `basic`, `quarantine`, `shop`, `communities`, `mobility_restrictions`

### Output

- **GIF Recording**: If `SAVE_GIF: true`, each frame is captured (sampled every `GIF_FRAME_INTERVAL` frames) and saved as `{RESULTS_DIR}/epidemia_{SCENARIO_NAME}.gif`
- **Plot**: After simulation ends, matplotlib displays and saves a plot of S/I/R counts over time to `{RESULTS_DIR}/wykres_{SCENARIO_NAME}.png`
- Output directory is created automatically by `GifRecorder` and `show_plot()`

## Extending the Simulation

### Adding a New Scenario

1. Create `simulation/scenarios/your_scenario.py` — class inherits `BaseScenario`, override only what changes
2. Create `config/scenarios/your_scenario.yaml` — only parameters that differ from `config/base.yaml`
3. Register in `simulation/scenarios/registry.py` — add an `if name == "your_scenario":` branch
4. Set `selected_scenario: your_scenario` in `config.yaml` to activate it

### Modifying Model Behavior

- **Change infection dynamics**: Adjust `INFECTION_RADIUS`, `INFECTION_PROBABILITY`, `RECOVERY_TIME` in `config.yaml`
- **Tune population**: Edit `POPULATION_SIZE`, `INITIAL_INFECTED`, `SPEED`
- **Add agent attributes**: Extend `Person.__init__()` and initialize in `SimulationModel.__init__()` or scenario-specific setup
- **Control frame capture rate**: Adjust `GIF_FRAME_INTERVAL` (higher = fewer frames in GIF)

## Key Design Patterns

- **Scenario Pattern**: `BaseScenario` defines the interface; subclasses override only what changes
- **Plugin Registry**: `get_scenario()` factory for dynamic scenario loading; error message auto-enumerates available YAML files
- **`initialize(model)` hook**: Called once in `SimulationModel.__init__()` after population creation — used by scenarios that need to set per-person state (e.g., `ShopScenario`, `CommunitiesScenario`)
- **`simulation/utils.py`**: `distance(ax, ay, bx, by)` — shared Euclidean distance helper used across model and scenarios
- **`Status` class** (`simulation/person.py`): String constants `Status.S`, `Status.I`, `Status.R` used everywhere instead of raw literals
- **History Tracking**: `SimulationModel.history` dict allows post-simulation plotting

## Documentation

`project-report-template/` contains the project report written in LaTeX (Overleaf format).

## Dependencies

See `requirements.txt`:
- pygame: GUI and visualization
- numpy: Numerical operations
- matplotlib: Plotting
- Pillow: Image processing for GIF export
- PyYAML: Configuration parsing

All dependencies are pinned to specific versions for reproducibility.
