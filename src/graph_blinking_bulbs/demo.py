from .model import BulbGraph, BulbState


def render(states: dict[int, BulbState]) -> str:
    symbol = {
        BulbState.OFF: ".",
        BulbState.ON: "*",
        BulbState.REFRACTORY: "x",
    }
    return " ".join(symbol[states[i]] for i in sorted(states))


def main() -> None:
    sim = BulbGraph.path(12, refractory_steps=2)
    sim.stimulate(0)

    print("Legend: *=ON, x=REFRACTORY, .=OFF")
    print(f"t={sim.time:02d}  {render(sim.states())}")

    for _ in range(15):
        sim.step()
        print(f"t={sim.time:02d}  {render(sim.states())}")


if __name__ == "__main__":
    main()
