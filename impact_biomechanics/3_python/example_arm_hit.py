"""Arm hit on Rajagopal2016: force pulse on right upper arm -> peak shoulder/elbow reaction force.
Run: python example_arm_hit.py
"""
import glob
import os
import time

import numpy as np
import opensim as osim

osim.Logger.setLevelString("warn")

F_PEAK = 2000.0        # N, take the real range from published tackle-force studies
PULSE_START = 0.02     # s
PULSE_WIDTH = 0.03     # s, triangular pulse
HIT_POINT = (0.0, -0.15, 0.0)   # m, in humerus_r frame (mid upper arm)
HIT_DIR = (0.0, 0.0, -1.0)      # ground frame: -Z = from the right side toward the body
DURATION = 0.15        # s
DT = 0.001             # s


def load_model():
    path = glob.glob(os.path.expanduser(r"~\Documents\OpenSim\*\Models\Rajagopal\Rajagopal2016.osim"))[0]
    model = osim.Model(path)

    shape = ((0, 0), (PULSE_START, 0), (PULSE_START + PULSE_WIDTH / 2, 1),
             (PULSE_START + PULSE_WIDTH, 0), (DURATION, 0))
    force_fns = []
    for d in HIT_DIR:
        fn = osim.PiecewiseLinearFunction()
        for t, s in shape:
            fn.addPoint(t, s * F_PEAK * d)
        force_fns.append(fn)

    hit = osim.PrescribedForce("hit", model.getBodySet().get("humerus_r"))
    hit.setForceIsInGlobalFrame(True)
    hit.setPointIsInGlobalFrame(False)
    hit.setForceFunctions(*force_fns)
    hit.setPointFunctions(*(osim.Constant(p) for p in HIT_POINT))
    model.addForce(hit)
    model.finalizeConnections()
    return model


def joint_for_child(model, body_name):
    for j in model.getJointSet():
        if j.getChildFrame().findBaseFrame().getName() == body_name:
            return j
    raise KeyError(body_name)


def main():
    model = load_model()
    state = model.initSystem()

    # ponytail: pelvis pinned to ground, fine for a ~30 ms hit; free-floating body + ground contact when it matters
    for name in ("pelvis_tilt", "pelvis_list", "pelvis_rotation", "pelvis_tx", "pelvis_ty", "pelvis_tz"):
        model.getCoordinateSet().get(name).setLocked(state, True)
    model.equilibrateMuscles(state)

    joints = {"shoulder": joint_for_child(model, "humerus_r"), "elbow": joint_for_child(model, "ulna_r")}
    peaks = {k: 0.0 for k in joints}

    manager = osim.Manager(model)
    state.setTime(0)
    manager.initialize(state)

    t0 = time.perf_counter()
    for t in np.arange(DT, DURATION + DT / 2, DT):
        state = manager.integrate(t)
        model.realizeAcceleration(state)
        for k, j in joints.items():
            f = j.calcReactionOnChildExpressedInGround(state).get(1)
            peaks[k] = max(peaks[k], float(np.linalg.norm([f.get(0), f.get(1), f.get(2)])))
    wall = time.perf_counter() - t0

    osim.STOFileAdapter.write(manager.getStatesTable(), "arm_hit_states.sto")
    bw = model.getTotalMass(state) * 9.81
    print(f"Hit: {F_PEAK:.0f} N triangular pulse, {PULSE_WIDTH * 1000:.0f} ms, on humerus_r")
    for k, j in joints.items():
        print(f"Peak {k} ({j.getName()}) reaction: {peaks[k]:.0f} N  = {peaks[k] / bw:.2f} x body weight")
    print(f"Wall time per case: {wall:.1f} s")


if __name__ == "__main__":
    main()
