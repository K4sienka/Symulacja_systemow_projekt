def get_scenario(name):
    if name == "basic":
        from simulation.scenarios.basic import BasicScenario
        return BasicScenario()

    if name == "quarantine":
        from simulation.scenarios.quarantine import QuarantineScenario
        return QuarantineScenario()

    if name == "shop":
        from simulation.scenarios.shop import ShopScenario
        return ShopScenario()

    if name == "communities":
        from simulation.scenarios.communities import CommunitiesScenario
        return CommunitiesScenario()

    if name == "mobility_restrictions":
        from simulation.scenarios.mobility_restrictions import MobilityRestrictionsScenario
        return MobilityRestrictionsScenario()

    if name == "social_distancing":
        from simulation.scenarios.social_distancing import SocialDistancingScenario
        return SocialDistancingScenario()

    from pathlib import Path
    available = sorted(
        p.stem
        for p in (Path(__file__).parents[2] / "config" / "scenarios").glob("*.yaml")
    )
    raise ValueError(f"Nieznany scenariusz: '{name}'. Dostępne: {', '.join(available)}")
