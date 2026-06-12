"""
Check whether OpenAeroStruct/OpenMDAO are installed.
Run:
    python scripts/check_openaerostruct_install.py
"""

import sys

print("Python executable:", sys.executable)
print("Python version:", sys.version)

try:
    import openmdao
    print("OpenMDAO import: OK")
    print("OpenMDAO version:", getattr(openmdao, "__version__", "unknown"))
except Exception as exc:
    print("OpenMDAO import: FAILED")
    print(exc)
    raise SystemExit(1)

try:
    import openaerostruct
    print("OpenAeroStruct import: OK")
    print("OpenAeroStruct version:", getattr(openaerostruct, "__version__", "unknown"))
except Exception as exc:
    print("OpenAeroStruct import: FAILED")
    print(exc)
    raise SystemExit(1)

print("Install check passed.")
