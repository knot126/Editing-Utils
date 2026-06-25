/**
 * clang -o clip clip.c -lavcodec -lavformat
 */

#include <stdio.h>
#include <string.h>
#include <stdint.h>

#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>

#define error(...) fprintf(stderr, __VA_ARGS__); exit(1);

FILE *open_cuts_file(const char *source_path) {
	char dest_path[strlen(source_path) + 5 + 1];
	strcpy(dest_path, source_path);
	
	// Remove extension from base filename
	for (size_t i = strlen(dest_path) - 1;; i--) {
		if (dest_path[i] == '.') {
			dest_path[i] = '\0';
			break;
		}
		
		if (i == 0 || dest_path[i] == '/') {
			break;
		}
	}
	
	strcat(dest_path, ".cuts");
	
	return fopen(dest_path, "wb");
}

int main(int argc, const char *argv[]) {
	if (argc < 2) {
		error("Not enough arguments!\nUsage: %s <file>\n", argv[0]);
	}
	
	int ret = 0;
	AVFormatContext *format_context = NULL;
	AVPacket *packet = NULL;
	
	char input_file[5 + strlen(argv[1]) + 1];
	strcpy(input_file, "file:");
	strcat(input_file, argv[1]);
	
	packet = av_packet_alloc();
	if (!packet) {
		error("av_packet_alloc failed\n");
	}
	
	ret = avformat_open_input(&format_context, input_file, NULL, NULL);
	
	if (ret != 0) {
		error("avformat_open_input failed: %d\n", ret);
	}
	
	ret = avformat_find_stream_info(format_context, NULL);
	
	if (ret != 0) {
		error("avformat_find_stream_info failed: %d\n", ret);
	}
	
	double audio_sample_time = 0.0;
	uint32_t audio_stream_index = 0;
	
	for (uint32_t i = 0; i < format_context->nb_streams; i++) {
		if (format_context->streams[i]->codecpar->codec_type == AVMEDIA_TYPE_AUDIO) {
			audio_stream_index = format_context->streams[i]->index;
			audio_sample_time = ((double)format_context->streams[i]->time_base.num)/((double)format_context->streams[i]->time_base.den);
		}
	}
	
	printf("audio stream index = %u, audio sample time = %.5f (%.2f samples/sec)\n", audio_stream_index, audio_sample_time, 1.0f/audio_sample_time);
	
	av_packet_free(&packet);
	avformat_close_input(&format_context);
	
	return 0;
}
