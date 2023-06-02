import os
import sys

reponse = os.popen(f"ping -c 4 {sys.argv[1]} ").read()

print(reponse)