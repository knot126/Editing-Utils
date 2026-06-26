#!/usr/bin/env python3
import subprocess
import tempfile
import os
import xml.sax.saxutils as xml

from argparse import ArgumentParser

# im too lazy to do it properly
FPS = 30.0

def find_silence(filename, db, spacing):
	ffmpeg_command = [
		"ffmpeg",
		"-i", filename,
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
	parser = ArgumentParser('generate_cuts', description="generate mlt file of video without silent points")
	parser.add_argument('-t', '--threshold', type=int, default=-35, help="The minium volume that will not be considered silence in dB; positive values are converted to negative values")
	parser.add_argument('-p', '--padding', type=float, default=100.0, help="How much additional time to add before and after noise regions in ms")
	parser.add_argument('-s', '--silence-time', type=str, default="300ms", help="The minium time needed for a clip of video to count as silent, as an ffmepg timestamp")
	parser.add_argument('-i', '--invert', action='store_true', help="Keep silent bits instead")
	parser.add_argument('input', help="Input video file")
	args = parser.parse_args()
	
	args.threshold = -abs(args.threshold)
	args.padding /= 1000
	video_file = args.input
	
	keep_bits = [0.0] + find_silence(video_file, args.threshold, args.silence_time) + [duration(video_file)]
	if args.invert: keep_bits = keep_bits[1:-1]
	
	keep_bits = polish_list(keep_bits)
	add_padding(keep_bits, args.padding)
	points = ""
	
	for i in range(0, len(keep_bits), 2):
		fin = int(keep_bits[i]*FPS)
		fout = int(keep_bits[i+1]*FPS)
		points += f"\t\t<entry producer=\"producer0\" in=\"{fin}\" out=\"{fout}\"/>\n"
	
	print(f"""<mlt>
	<producer id="producer0">
		<property name="resource">{xml.escape(video_file)}</property>
	</producer>
	<playlist id="playlist0">
{points}
	</playlist>
</mlt>""")

if __name__ == "__main__":
	main()
