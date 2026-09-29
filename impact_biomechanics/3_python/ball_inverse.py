"""Inverse dynamics check for lesson 1: from the ball's motion alone, work back to the floor force.
Reads ball.osim + ball_states.sto (made by ball_bounce.py), writes outputs/ball_inverse.sto,
and compares the ID force with floor_force from the forward simulation.
Run: python ball_inverse.py   (run ball_bounce.py first)
"""
import os

import numpy as np
import opensim as osim

osim.Logger.setLevelString("warn")

HERE = os.path.dirname(os.path.abspath(__file__))
LESSON_DIR = os.path.join(HERE, "..", "1_lesson_opensim_gui")
OUT_DIR = os.path.join(HERE, "outputs")
OUT_FILE = "ball_inverse.sto"


def main():
    states_path = os.path.join(LESSON_DIR, "ball_states.sto")
    states = osim.TimeSeriesTable(states_path)
    times = np.array(states.getIndependentColumn())
    floor_force = states.getDependentColumn("floor_force").to_numpy()

    model = osim.Model(os.path.join(LESSON_DIR, "ball.osim"))  # keep this reference alive or the tool segfaults
    model.initSystem()

    tool = osim.InverseDynamicsTool()
    tool.setModel(model)
    tool.setCoordinatesFileName(states_path)  # only the ball_height column is used
    tool.setStartTime(times[0])
    tool.setEndTime(times[-1])
    tool.setLowpassCutoffFrequency(-1)  # no filtering: a 6.5 ms impact would be smoothed away
    excluded = osim.ArrayStr()
    excluded.append("contact")  # ID must supply the floor's push itself; leave contact in and the answer is ~0
    tool.setExcludedForces(excluded)
    tool.setResultsDir(OUT_DIR)
    tool.setOutputGenForceFileName(OUT_FILE)
    tool.run()

    id_force = osim.TimeSeriesTable(os.path.join(OUT_DIR, OUT_FILE)).getDependentColumn("ball_height_force").to_numpy()
    print(f"Peak floor force  forward: {floor_force.max():.0f} N   inverse: {id_force.max():.0f} N")
    assert abs(id_force.max() - floor_force.max()) < 5, "inverse dynamics should recover the forward peak force"
    print(f"Saved {os.path.normpath(os.path.join(OUT_DIR, OUT_FILE))}")


if __name__ == "__main__":
    main()
