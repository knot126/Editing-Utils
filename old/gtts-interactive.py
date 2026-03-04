#!/usr/bin/env python3
import subprocess
import os
import sys

def find_filename():
	files = set(os.listdir())
	
	n = 1
	
	while True:
		if f"{n}.mp3" not in files:
			return f"{n}.mp3"
		n += 1

def append_transcript(text):
	with open("transcript.txt", "a+") as f:
		f.write(text + "\n\n")

text = sys.argv[1]
name = find_filename()
subprocess.run(["gtts-cli", text, "--output", name], check=True)
append_transcript(f"{name}: {text}")
print(f"[saved as {name}]")

"""
try:
	print(f"Interactive wrapper for gtts-cli\nRunning in {os.getcwd()}\n")
	
	while True:
		text = input("> ")
		name = find_filename()
		subprocess.run(["gtts-cli", text, "--output", name], check=True)
		append_transcript(text)
		print(f"[saved as {name}]")
except KeyboardInterrupt:
	print("Quitting...")
"""
