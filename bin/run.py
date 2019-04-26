import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from core import QPcollect

if __name__ == "__main__":
    client = QPcollect.Collect(sys.argv)
    client.forever_run()
