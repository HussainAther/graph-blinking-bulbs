# Graph Blinking Bulbs

Starter implementation for Dr. Richard Gordon's question:

> How does a graph react if each node may be a blinking bulb and electricity is passed between two nodes?

The code models each graph node as an excitable bulb with three states:
`OFF`, `ON`, and `REFRACTORY`.

## Install for development

```bash
python -m pip install -e ".[dev]"
```

## Run demo

```bash
python -m graph_blinking_bulbs.demo
```

## Run tests

```bash
pytest
```

## First experiments

- Compare paths, rings, and stars.
- Stimulate two nodes and observe wave-front collisions.
- Increase activation threshold.
- Change refractory duration.
- Search small graphs for periodic activity.

See `ROADMAP.md` for next steps.
