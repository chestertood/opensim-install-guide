"""Environment check for student 2 (impact_biomechanics) before Sunday session.
Run: python check_env.py
"""
import glob
import os
import sys


def check_python():
    v = sys.version_info
    print(f"[Python] {v.major}.{v.minor}.{v.micro}")
    if v.major != 3 or not (11 <= v.minor <= 13):
        print("  WARN: opensim PyPI wheels (4.6+) target Python 3.11-3.13.")


def check_opensim():
    try:
        import opensim
    except ImportError as e:
        print(f"[opensim] FAIL - not importable: {e}")
        print("  Fix: activate the opensim_env venv (Python 3.11) then `pip install opensim`")
        return None
    print(f"[opensim] OK - version {opensim.__version__}")
    return opensim


def find_gait2392():
    patterns = [
        os.path.expanduser(r"~\Documents\OpenSim\*\Models\Gait2392_Simbody\gait2392_simbody.osim"),
        r"C:\OpenSim*\Models\Gait2392_Simbody\gait2392_simbody.osim",
        r"C:\Program Files\OpenSim*\Models\Gait2392_Simbody\gait2392_simbody.osim",
        os.path.expanduser(r"~\OpenSim*\Models\Gait2392_Simbody\gait2392_simbody.osim"),
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    return None


def check_model_load(opensim):
    path = find_gait2392()
    if not path:
        print("[gait2392] FAIL - model file not found in default install locations")
        print("  Fix: check where the OpenSim GUI installed Models\\Gait2392_Simbody\\gait2392_simbody.osim")
        return
    print(f"[gait2392] found: {path}")
    try:
        model = opensim.Model(path)
        state = model.initSystem()
        print(f"[gait2392] OK - loaded, {model.getBodySet().getSize()} bodies, {model.getMuscles().getSize()} muscles")
    except Exception as e:
        print(f"[gait2392] FAIL - could not load/init: {e}")


def main():
    check_python()
    opensim = check_opensim()
    if opensim is not None:
        check_model_load(opensim)


if __name__ == "__main__":
    main()
