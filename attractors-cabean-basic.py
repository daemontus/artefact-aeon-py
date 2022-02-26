import sys
import os

from pathlib import Path

model_path = sys.argv[1].replace("aeon", "bnet")
print("Model path", model_path)

code = os.system('CABEAN-release-2.0.1/BinaryFile/WindowsLinux/cabean_linux ' + model_path)
print("Exit code", code)
exit(code)
