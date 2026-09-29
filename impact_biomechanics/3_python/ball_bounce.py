"""Bouncing basketball for lesson 1: builds ball.osim + ball_states.sto in 1_lesson_opensim_gui/.
ball_states.sto columns: ball_height (m, ball centre), ball_speed (m/s), ball_accel (m/s^2), floor_force (N).
Run: python ball_bounce.py
"""
import os

import numpy as np
import opensim as osim

osim.Logger.setLevelString("warn")

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "1_lesson_opensim_gui")

BALL_MASS = 0.6        # kg, basketball
BALL_RADIUS = 0.12     # m
DROP_HEIGHT = 1.0      # m, bottom of ball above floor
STIFFNESS = 1e7        # Pa (Hunt-Crossley, Young's-modulus-like); ball sinks ~9 mm into floor, like a real ball squashing
DISSIPATION = 0.05     # s/m, 1 m drop -> ~0.67 m bounce like a real basketball; higher = deader ball
DURATION = 10          # s
MAX_STEP = 0.005       # s, longest integrator step
FLOOR_Y = 0.05         # m, top of our floor slab: sits above the GUI's own ground plane (y = 0) so the two don't flicker through each other
FLOOR_HALF = (1.0, 1.0)   # m, floor visual half-length (X) and half-width (Z): 2 x 2 m, fits the GUI view without zooming
SAMPLE_DT = 0.001      # s, one row per ms: even spacing so GUI playback runs at a steady speed (~6 rows per impact)


def new_model(name):
    """Empty model with gravity plus the orange ball body (no joint yet)."""
    model = osim.Model()
    model.setName(name)
    model.setGravity(osim.Vec3(0, -9.81, 0))

    inertia = 2 / 3 * BALL_MASS * BALL_RADIUS ** 2  # hollow sphere
    ball = osim.Body("ball", BALL_MASS, osim.Vec3(0), osim.Inertia(inertia))
    sphere = osim.Sphere(BALL_RADIUS)
    sphere.setColor(osim.Vec3(0.9, 0.45, 0.1))
    ball.attachGeometry(sphere)
    model.addBody(ball)
    return model, ball


def build_model():
    model, ball = new_model("bouncing_ball")

    # Slider along ground Y: rotate joint frame 90 deg about Z so its X axis points up.
    joint = osim.SliderJoint("up_down", model.getGround(), osim.Vec3(0), osim.Vec3(0, 0, np.pi / 2),
                             ball, osim.Vec3(0), osim.Vec3(0, 0, np.pi / 2))
    coord = joint.upd_coordinates(0)
    coord.setName("ball_height")
    coord.setRangeMin(0.0)
    coord.setRangeMax(3.0)
    coord.setDefaultValue(FLOOR_Y + DROP_HEIGHT + BALL_RADIUS)  # GUI starts here
    model.addJoint(joint)

    add_floor(model, ball)
    model.finalizeConnections()
    return model, coord


def add_floor(model, ball, static_friction=0.0, dynamic_friction=0.0, floor_half=FLOOR_HALF):
    """Grey floor visual + Hunt-Crossley contact between ball and floor (force named "contact")."""
    # Slab from y = 0 up to FLOOR_Y (brick is centred on its frame): top face = contact plane.
    floor_visual = osim.Brick(osim.Vec3(floor_half[0], FLOOR_Y / 2, floor_half[1]))
    floor_visual.setColor(osim.Vec3(0.6, 0.6, 0.6))
    floor_frame = osim.PhysicalOffsetFrame("floor_visual", model.getGround(), osim.Transform(osim.Vec3(0, FLOOR_Y / 2, 0)))
    floor_frame.attachGeometry(floor_visual)
    model.addComponent(floor_frame)

    floor = osim.ContactHalfSpace(osim.Vec3(0, FLOOR_Y, 0), osim.Vec3(0, 0, -np.pi / 2), model.getGround(), "floor")
    ball_contact = osim.ContactSphere(BALL_RADIUS, osim.Vec3(0), ball, "ball_contact")
    model.addContactGeometry(floor)
    model.addContactGeometry(ball_contact)

    contact = osim.HuntCrossleyForce()
    contact.setName("contact")
    contact.addGeometry("ball_contact")
    contact.addGeometry("floor")
    contact.setStiffness(STIFFNESS)
    contact.setDissipation(DISSIPATION)
    contact.setStaticFriction(static_friction)
    contact.setDynamicFriction(dynamic_friction)
    contact.setViscousFriction(0)
    model.addForce(contact)


def simulate(model, coord):
    state = model.initSystem()
    manager = osim.Manager(model)
    manager.setIntegratorAccuracy(1e-6)
    manager.setIntegratorMaximumStepSize(MAX_STEP)
    state.setTime(0)
    manager.initialize(state)

    # Stop the integrator every SAMPLE_DT and record: evenly spaced rows. (One row per integrator step
    # bunched ~35 rows into each 6.5 ms impact, so frame-by-frame playback stalled on every bounce.)
    contact = model.getForceSet().get("contact")
    table = osim.TimeSeriesTable()
    table.setColumnLabels(["ball_height", "ball_speed", "ball_accel", "floor_force"])
    table.addTableMetaDataString("inDegrees", "no")
    rows = []
    for t in np.arange(0, round(DURATION / SAMPLE_DT) + 1) * SAMPLE_DT:
        if t > 0:
            state = manager.integrate(t)
        model.realizeAcceleration(state)
        force_up = contact.getRecordValues(state).get(1)  # contact.ball.force.Y = push of floor on ball
        row = [coord.getValue(state), coord.getSpeedValue(state), coord.getAccelerationValue(state), force_up]
        table.appendRow(state.getTime(), osim.RowVector(row))
        rows.append(row)
    return table, np.array(rows)


def bounce_peaks(speed, force):
    """Bounce heights from take-off speed (h = v^2 / 2g, exact in free flight; air samples are too sparse to catch the apex)."""
    takeoff = np.where((force[:-1] > 0) & (force[1:] == 0))[0] + 1
    peaks = speed[takeoff] ** 2 / (2 * 9.81)
    return [p for p in peaks if p > 0.01]  # ignore jitter once the ball settles on the floor


def main():
    model, coord = build_model()
    osim_path = os.path.join(OUT_DIR, "ball.osim")
    model.printToXML(osim_path)

    table, data = simulate(model, coord)
    osim.STOFileAdapter.write(table, os.path.join(OUT_DIR, "ball_states.sto"))

    peaks = bounce_peaks(data[:, 1], data[:, 3])
    print(f"Drop height {DROP_HEIGHT:.2f} m -> bounce peaks: " + ", ".join(f"{p:.2f}" for p in peaks[:5]) + " m")
    assert peaks and peaks[0] < DROP_HEIGHT, "ball should bounce lower than it was dropped"
    assert all(a > b for a, b in zip(peaks, peaks[1:])), "each bounce should be lower than the last"
    assert np.allclose(np.diff(table.getIndependentColumn()), SAMPLE_DT), "rows must be evenly spaced for smooth playback"
    print(f"Saved {os.path.normpath(osim_path)} and ball_states.sto")


if __name__ == "__main__":
    main()
