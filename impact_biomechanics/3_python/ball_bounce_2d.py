"""Bounce pass: basketball thrown along the floor, floor pushes back in 3 axes (up + friction in X and Z).
Ball slides in X, Y, Z only (no spin). Throw direction: +/- X and +/- Z via THROW_SPEED (or the coordinates'
default speed in the GUI).
Builds ball_2d.osim + ball_2d_states.sto in 1_lesson_opensim_gui/.
ball_2d_states.sto columns: ball_x, ball_y, ball_z (m), ball_x_speed, ball_y_speed, ball_z_speed (m/s),
force_x, force_z (friction, N), force_y (floor push up, N).
Run: python ball_bounce_2d.py
"""
import os

import numpy as np
import opensim as osim

from ball_bounce import BALL_RADIUS, DROP_HEIGHT, FLOOR_Y, MAX_STEP, OUT_DIR, SAMPLE_DT, add_floor, new_model

THROW_SPEED = (3.0, 0.0, 0.0)  # m/s (X, Y up, Z): 0 = plain drop; bounce pass e.g. (4, -3, 0), any +/- X or Z works
STATIC_FRICTION = 0.2      # low: ball cannot spin here, so 0.8 would stop the slide dead on the 1st bounce; 0 = ice
DYNAMIC_FRICTION = 0.15
FLOOR_HALF = (10.0, 10.0)    # m, floor visual half-length (X, direction of travel) and half-width (Z); (3.0, 1.0) = 6 m long
DURATION = 10              # s; floor visual is only a picture: contact plane is infinite, so the ball never falls off

AXES = ["ball_x", "ball_y", "ball_z"]
COLUMNS = AXES + [a + "_speed" for a in AXES] + ["force_x", "force_y", "force_z"]


def build_model():
    model, ball = new_model("bounce_pass")

    # Custom joint with 3 slides (X forward, Y up, Z sideways) and no rotation: the ball cannot spin.
    st = osim.SpatialTransform()
    for i, (name, axis) in enumerate(zip(AXES, [(1, 0, 0), (0, 1, 0), (0, 0, 1)])):
        ax = st.updTransformAxis(3 + i)  # axes 0-2 are rotations (left unused), 3-5 translations
        ax.setCoordinateNames(osim.ArrayStr(name, 1))
        ax.setAxis(osim.Vec3(*axis))
        ax.set_function(osim.LinearFunction())  # set_ copies; setFunction double-frees in Python
    model.addJoint(osim.CustomJoint("bounce_pass", model.getGround(), ball, st))

    add_floor(model, ball, STATIC_FRICTION, DYNAMIC_FRICTION, FLOOR_HALF)
    model.finalizeConnections()
    coords = [model.getCoordinateSet().get(name) for name in AXES]
    for c, speed in zip(coords, THROW_SPEED):
        c.setRangeMin(-20.0)
        c.setRangeMax(20.0)
        c.setDefaultSpeedValue(speed)  # GUI Forward Dynamics starts with the throw too
    coords[1].setRangeMin(0.0)
    coords[1].setRangeMax(3.0)
    coords[1].setDefaultValue(FLOOR_Y + DROP_HEIGHT + BALL_RADIUS)
    return model, coords


def simulate(model, coords):
    state = model.initSystem()
    manager = osim.Manager(model)
    manager.setIntegratorAccuracy(1e-6)
    manager.setIntegratorMaximumStepSize(MAX_STEP)
    state.setTime(0)
    manager.initialize(state)

    contact = model.getForceSet().get("contact")
    table = osim.TimeSeriesTable()
    table.setColumnLabels(COLUMNS)
    table.addTableMetaDataString("inDegrees", "no")
    rows = []
    for t in np.arange(0, round(DURATION / SAMPLE_DT) + 1) * SAMPLE_DT:
        if t > 0:
            state = manager.integrate(t)
        model.realizeAcceleration(state)
        rec = contact.getRecordValues(state)  # contact.ball.force.X, .Y, ... = push of floor on ball
        row = ([c.getValue(state) for c in coords] + [c.getSpeedValue(state) for c in coords]
               + [rec.get(0), rec.get(1), rec.get(2)])
        table.appendRow(state.getTime(), osim.RowVector(row))
        rows.append(row)
    return table, np.array(rows)


def main():
    model, coords = build_model()
    osim_path = os.path.join(OUT_DIR, "ball_2d.osim")
    model.printToXML(osim_path)

    table, data = simulate(model, coords)
    osim.STOFileAdapter.write(table, os.path.join(OUT_DIR, "ball_2d_states.sto"))

    x, z, vx, vz = data[:, 0], data[:, 2], data[:, 3], data[:, 5]
    fx, fy, fz = data[:, 6], data[:, 7], data[:, 8]
    first = np.argmax(fy > 0)
    hit = slice(first, first + np.argmax(fy[first:] == 0))
    print(f"First impact at t={first * SAMPLE_DT:.3f} s: peak force_y {fy[hit].max():.0f} N, "
          f"friction force_x {fx[hit].min():.0f}..{fx[hit].max():.0f} N, force_z {fz[hit].min():.0f}..{fz[hit].max():.0f} N")
    print(f"Speed X {vx[0]:.2f} -> {vx[hit.stop]:.2f}, Z {vz[0]:.2f} -> {vz[hit.stop]:.2f} m/s after first bounce; "
          f"ball ends at x={x[-1]:.2f}, z={z[-1]:.2f} m")

    # Friction pushes against the slide in each axis: sign of force opposite to sign of throw speed.
    for f, v0, v1, name in [(fx, vx[0], vx[hit.stop], "X"), (fz, vz[0], vz[hit.stop], "Z")]:
        if abs(v0) > 0.01:
            assert np.sign(f[hit].sum()) == -np.sign(v0), f"friction in {name} should push against the throw"
            assert abs(v1) < abs(v0), f"friction should slow the ball in {name}"
    print(f"Saved {os.path.normpath(osim_path)} and ball_2d_states.sto")


if __name__ == "__main__":
    main()
