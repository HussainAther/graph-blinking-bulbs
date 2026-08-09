from graph_blinking_bulbs import BulbGraph, BulbState


def test_path_propagates_one_node_per_step():
    sim = BulbGraph.path(4, refractory_steps=1)
    sim.stimulate(0)

    assert sim.active_nodes() == {0}

    sim.step()
    assert sim.active_nodes() == {1}

    sim.step()
    assert sim.active_nodes() == {2}

    sim.step()
    assert sim.active_nodes() == {3}


def test_threshold_can_block_single_input():
    sim = BulbGraph.path(3, threshold=2, refractory_steps=1)
    sim.stimulate(0)

    sim.step()
    assert sim.active_nodes() == set()


def test_two_neighbors_can_meet_threshold():
    adjacency = {
        0: {2},
        1: {2},
        2: {0, 1},
    }
    sim = BulbGraph(adjacency, threshold=2, refractory_steps=1)
    sim.stimulate(0, 1)

    sim.step()
    assert sim.active_nodes() == {2}


def test_refractory_prevents_immediate_refire():
    sim = BulbGraph.path(2, refractory_steps=2)
    sim.stimulate(0)

    sim.step()
    assert sim.states()[0] is BulbState.REFRACTORY
    assert sim.states()[1] is BulbState.ON

    sim.step()
    assert sim.states()[0] is BulbState.REFRACTORY

    sim.step()
    assert sim.states()[0] is BulbState.OFF
