"""Head drop test: build a model in code, run forward dynamics, compute peak g and HIC15.
Run: python example_drop_test.py
"""
import numpy as np
import opensim as osim

osim.Logger.setLevelString("warn")

DROP_HEIGHT = 1.0      # m
HEAD_MASS = 4.5        # kg, roughly an adult head
HEAD_RADIUS = 0.09     # m
STIFFNESS = 1e7        # N/m, contact stiffness (tune: softer = longer contact = lower HIC)
DISSIPATION = 0.5      # s/m
DURATION = 0.6         # s
DT = 0.0002            # s, output sampling


def build_model():
    model = osim.Model()
    model.setName("head_drop")
    model.setGravity(osim.Vec3(0, -9.81, 0))

    head = osim.Body("head", HEAD_MASS, osim.Vec3(0), osim.Inertia(0.02))
    model.addBody(head)

    # Slider along ground Y: rotate joint frame 90 deg about Z so its X axis points up.
    joint = osim.SliderJoint("drop", model.getGround(), osim.Vec3(0), osim.Vec3(0, 0, np.pi / 2),
                             head, osim.Vec3(0), osim.Vec3(0, 0, np.pi / 2))
    model.addJoint(joint)

    floor = osim.ContactHalfSpace(osim.Vec3(0), osim.Vec3(0, 0, -np.pi / 2), model.getGround(), "floor")
    sphere = osim.ContactSphere(HEAD_RADIUS, osim.Vec3(0), head, "head_sphere")
    model.addContactGeometry(floor)
    model.addContactGeometry(sphere)

    contact = osim.HuntCrossleyForce()
    contact.setName("contact")
    contact.addGeometry("head_sphere")
    contact.addGeometry("floor")
    contact.setStiffness(STIFFNESS)
    contact.setDissipation(DISSIPATION)
    contact.setStaticFriction(0)
    contact.setDynamicFriction(0)
    contact.setViscousFriction(0)
    model.addForce(contact)

    model.finalizeConnections()
    return model, joint


def simulate(model, joint):
    state = model.initSystem()
    coord = joint.getCoordinate()
    coord.setValue(state, DROP_HEIGHT + HEAD_RADIUS)

    manager = osim.Manager(model)
    manager.setIntegratorAccuracy(1e-6)
    state.setTime(0)
    manager.initialize(state)

    times = np.arange(0, DURATION, DT)
    y, v = [coord.getValue(state)], [coord.getSpeedValue(state)]
    for t in times[1:]:
        state = manager.integrate(t)
        y.append(coord.getValue(state))
        v.append(coord.getSpeedValue(state))
    osim.STOFileAdapter.write(manager.getStatesTable(), "head_drop_states.sto")
    return times, np.array(y), np.array(v)


def hic(t, a_g, max_window=0.015):
    """HIC over windows up to max_window seconds. a_g = resultant acceleration in g."""
    cum = np.concatenate([[0.0], np.cumsum((a_g[1:] + a_g[:-1]) / 2 * np.diff(t))])
    best = 0.0
    for i in range(len(t)):
        j = np.searchsorted(t, t[i] + max_window + 1e-12, side="right")
        width = t[i + 1:j] - t[i]
        if len(width):
            avg = (cum[i + 1:j] - cum[i]) / width
            best = max(best, float(np.max(width * avg ** 2.5)))
    return best


def main():
    model, joint = build_model()
    model.printToXML("head_drop.osim")  # open in OpenSim GUI to see it

    t, y, v = simulate(model, joint)
    a_g = np.abs(np.gradient(v, t)) / 9.81

    print(f"Impact speed ~ {abs(v.min()):.2f} m/s (theory {np.sqrt(2 * 9.81 * DROP_HEIGHT):.2f})")
    print(f"Peak acceleration: {a_g.max():.0f} g")
    print(f"HIC15: {hic(t, a_g):.0f}   (risk threshold 700)")

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 1, sharex=True, figsize=(7, 7))
    for axis, data, label in zip(ax, (y, v, a_g), ("height (m)", "velocity (m/s)", "acceleration (g)")):
        axis.plot(t, data)
        axis.set_ylabel(label)
    ax[-1].set_xlabel("time (s)")
    fig.tight_layout()
    fig.savefig("head_drop.png", dpi=120)
    print("Saved head_drop.png, head_drop_states.sto (GUI: File > Load Motion)")


if __name__ == "__main__":
    t = np.arange(0, 0.1, 0.0001)
    assert abs(hic(t, np.full_like(t, 100.0)) - 1500) < 15, "HIC self-check failed"
    main()
