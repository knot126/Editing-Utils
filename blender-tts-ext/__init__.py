import bpy
import subprocess
import os

from pathlib import Path
from bpy.props import IntProperty, StringProperty

CLASSES_TO_LOAD = []

def registered(cls):
	CLASSES_TO_LOAD.append(cls)
	return cls

def generate_tts_file(path, text):
	subprocess.run(["gtts-cli", text, "--output", path], check=True)

def add_strip_at_marker_with_channel_for_context(context, channel, path):
	context.sequencer_scene.sequence_editor.strips.new_sound(path.split("/")[-1].replace(".", "_"), path, channel, context.sequencer_scene.frame_current)

def find_filename(path):
	i = 0
	files = os.listdir(path)
	
	while True:
		i += 1
		
		if f"tts{i}.mp3" not in files:
			return f"{path}/tts{i}.mp3"

@registered
class GenerateTTSClip(bpy.types.Operator):
	"""Generate a TTS audio file from given text, then insert it into the scene"""
	
	bl_idname = "tts.generate"
	bl_label = "Insert TTS"
	bl_options = {'REGISTER', 'UNDO'}
	
	channel: IntProperty(
		name="Channel ID",
		description="Which channel should the tts clip be inserted into after its done generating",
		default=3,
	)
	
	text: StringProperty(
		name="Text",
		description="Text to convert to speech",
		default="",
	)
	
	def invoke(self, context, event):
		context.window_manager.invoke_props_dialog(self)
		return {'RUNNING_MODAL'}
	
	def execute(self, context):
		try:
			if not context.blend_data.filepath:
				raise Exception("Please save blend file before using TTS tool.")
			
			sound_dir = str(Path(context.blend_data.filepath).parent)
			sound_filepath = find_filename(sound_dir)
			
			generate_tts_file(sound_filepath, self.text)
			add_strip_at_marker_with_channel_for_context(context, self.channel, sound_filepath)
		except Exception as e:
			self.report({'ERROR'}, f"{type(e).__name__}: {e}")
		
		return {'FINISHED'}

def tts_clip_menu(self, context):
	self.layout.separator()
	self.layout.operator(GenerateTTSClip.bl_idname)

def register():
	for cls in CLASSES_TO_LOAD:
		bpy.utils.register_class(cls)
	
	bpy.types.SEQUENCER_MT_add.append(tts_clip_menu)

def unregister():
	for cls in reversed(CLASSES_TO_LOAD):
		bpy.utils.unregister_class(cls)
	
	bpy.types.SEQUENCER_MT_add.remove(tts_clip_menu)

if __name__ == "__main__":
	register()
