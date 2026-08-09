from graph_blinking_bulbs import BulbGraph


def summarize(name: str, sim: BulbGraph, source: int, steps: int = 10) -> None:
    sim.stimulate(source)
    history = sim.run(steps)

    print(f"\n{name}")
    for t, snapshot in enumerate(history):
        active = [node for node, state in snapshot.items() if state.value == "on"]
        print(f"t={t:02d}: active={active}")


def main() -> None:
    summarize("Path", BulbGraph.path(8, refractory_steps=2), source=0)
    summarize("Ring", BulbGraph.ring(8, refractory_steps=2), source=0)
    summarize("Star", BulbGraph.star(7, refractory_steps=2), source=0)


if __name__ == "__main__":
    main()
