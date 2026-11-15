"""Alternative I/O examples: all model/stimulus parameters come from model.yaml."""

from pathlib import Path
from flymodel import Model

root = Path(__file__).resolve().parents[1]
sim = Model(root / "01_model/model.yaml")
# Same frozen model, multiple preset input protocols. Custom event/current arrays
# can be passed to run_neural(events=..., current_waveform=...).
result = sim.run_neural("DN_drive")
ids = sim.neuron_ids(type="DNg100")
print(
    sim.state(
        ids, sim.config["experiments"]["DN_drive"]["events"][0]["on_ms"], result=result
    )
)
print(sim.connections(ids[0], direction="outgoing"))
u = sim.muscle_excitation(result)
body, trace = sim.simulate_body(result)
print(body.observe())
print(body.contacts())
# body.step(one_muscle_vector) is the independent muscle-drive interface.
# record_ids=None records every cell; a list restricts recording without
# altering integration. State access includes soma/axon, m/h/n, Ca, currents.
