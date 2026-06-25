#!/usr/bin/env python3
import subprocess
import tempfile
import sys
import os

# im too lazy to do it properly
FPS = 30.0
PADDING = (100/1000)

def find_silence(filename, db, spacing):
	ffmpeg_command = [
		"ffmpeg",
		"-i",filename,
		"-af", f"silencedetect=n={db}dB:d={spacing}",
		"-f", "null", "-"
	]
	
	output = str(subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
	lines = output.split("\\n")
	time_list = []

	for line in lines:
		if ("silencedetect" in line):
				words = line.split(" ")
				
				for i in range (len(words)):
					if "silence_start" in words[i]:
						time_list.append(float(words[i+1]))
					if "silence_end" in words[i]:
						time_list.append(float(words[i+1]))
	
	print(f"<!-- debug: {len(time_list) // 2} silent bits -->")
	
	return time_list

def duration(filename: str) -> float:
	command = ["ffprobe",
		"-i", filename,
		"-v", "quiet",
		"-show_entries", "format=duration",
		"-hide_banner",
		"-of", "default=noprint_wrappers=1:nokey=1"
	]
	
	output = subprocess.run(command, stdout=subprocess.PIPE)
	return float(str(output.stdout, "UTF-8"))

def polish_list(clips):
	new_clips = []
	
	for i in range(0, len(clips), 2):
		if (int(FPS*clips[i]) != int(FPS*clips[i+1])):
			new_clips.append(clips[i])
			new_clips.append(clips[i+1])
	
	return new_clips

def add_padding(clips, padding):
	padding /= 2
	
	for i in range(0, len(clips), 2):
		clips[i] -= padding
		clips[i+1] += padding

def main():
	video_file = sys.argv[1]
	
	keep_bits = [0.0] + find_silence(video_file, -35, "300ms") + [duration(video_file)]
	keep_bits = polish_list(keep_bits)
	add_padding(keep_bits, PADDING)
	points = ""
	
	for i in range(0, len(keep_bits), 2):
		fin = int(keep_bits[i]*FPS)
		fout = int(keep_bits[i+1]*FPS)
		points += f"\t\t<entry producer=\"producer0\" in=\"{fin}\" out=\"{fout}\"/>\n"
	
	print(f"""<mlt>
	<producer id="producer0">
		<property name="resource">{video_file}</property>
	</producer>
	<playlist id="playlist0">
{points}
	</playlist>
</mlt>""")

if __name__ == "__main__":
	main()
