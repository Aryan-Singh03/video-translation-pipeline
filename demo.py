import os
from translator import *

# change these to your input mp4, srt, and desired language
mp4_in = "Tanzania-2.mp4"
srt_in = "Tanzania-caption.srt"
language = "german"

translated_srt = "translated.srt"
ckpt_converter = 'OpenVoice/checkpoints_v2/converter'
translated_dir = f"intermediate_{language}_outputs"
reference_voice = os.path.join(translated_dir, "reference_voice.wav")
final_wav = os.path.join(translated_dir, f"cloned_{language}_wav.wav")
mp4_out = "translated_vid.mp4"


new_audio(mp4_in, srt_in, language, translated_dir, ckpt_converter, reference_voice, translated_srt, final_wav)
combine_audio_video(mp4_in, final_wav, mp4_out)
