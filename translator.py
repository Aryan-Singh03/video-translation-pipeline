import os
import subprocess
import asyncio
import torch
import pysrt
import langcodes
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment

def extract_audio(mp4_in, wav_out):
    subprocess.run(['ffmpeg', '-y', '-i', mp4_in, '-vn','-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '1', wav_out], capture_output=True, text=True)

def extract_video(mp4_in, mp4_na_out):
    video = subprocess.run(['ffmpeg', '-i', mp4_in, '-an', '-c:v', 'copy', mp4_na_out])

def get_ISO639(language: str):
    lang = langcodes.Language.find(language)
    return lang.to_tag()


async def translate(text, langcode):
    async with Translator() as translator:
        translated_text = await translator.translate(text, dest=langcode)
        return translated_text

# translating srt
async def parse(srt_in, srt_out, langcode):
    subs = pysrt.open(srt_in)
    subtitles = [sub.text for sub in subs]
    translated_texts =  await translate(subtitles, langcode)
    for i, translated_text in enumerate(translated_texts):
        subs[i].text = translated_text.text
    subs.save(srt_out)

# convert mp3 to wav
def mp3_to_wav_16k(inp_mp3, out_wav):
    subprocess.run(["ffmpeg", "-y", "-i", inp_mp3, "-ar", "16000", "-f", "wav", out_wav])

# convert srt time to ms
def time_to_ms(t):
    return t.hours*3600000 + t.minutes*60000 + t.seconds*1000 + int(t.milliseconds)

# speed up/slow down audio
def stretch_audio(in_wav, out_wav, target_ms):
    orig = AudioSegment.from_wav(in_wav)
    orig_ms = len(orig)
    time_ratio = target_ms / orig_ms
    cmd = ["rubberband", "-t", str(time_ratio), "-p", "0", "-c", "6", "-F", "--detector-soft", in_wav, out_wav]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

# mp4, srt, language -> translated_srt, translated_cloned_wav
def new_audio(mp4_in, srt_in, language, reference_voice, translated_srt, final_wav):
    langcode = get_ISO639(language)
    extract_audio(mp4_in, reference_voice) # extract audio file
    asyncio.run(parse(srt_in, translated_srt, langcode)) # translate srt
    translated_dir = f"{language}_output"

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")

    os.makedirs(translated_dir, exist_ok=True)

    # loading model
    tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
    tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

    # building speaker embedding from reference audiofile
    target_se, _ = se_extractor.get_se(reference_voice, tone_color_converter, vad=True)

    # creating source sample using gTTS and extracting source speaker embedding
    source_sample_mp3 = os.path.join(translated_dir, "translated_tts_sample.mp3")
    source_sample_wav = os.path.join(translated_dir, "translated_tts_sample.wav")
    subs = pysrt.open(translated_srt)
    gTTS(text=subs.text.replace('\n', ' '), lang=langcode).save(source_sample_mp3)
    mp3_to_wav_16k(source_sample_mp3, source_sample_wav)
    os.remove(source_sample_mp3)
    source_se, _ = se_extractor.get_se(source_sample_wav, tone_color_converter, vad=True)

    timeline = None
    fr = ch = sw = None
    current_pos_ms = 0
    for i, sub in enumerate(subs, start=1):
        # clean srt text
        text = sub.text.replace("\n", " ").strip()
        
        # using base gtts to produce german mp3 and converting to wav
        base_mp3 = os.path.join(translated_dir, f"base_{i:04d}.mp3")
        gTTS(text=text, lang=langcode).save(base_mp3)
        base_wav = os.path.join(translated_dir, f"base_{i:04d}.wav")
        mp3_to_wav_16k(base_mp3, base_wav)
        os.remove(base_mp3)
        
        # modifying voice to match reference
        cloned_wav = os.path.join(translated_dir, f"cloned_{i:04d}.wav")
        tone_color_converter.convert(audio_src_path=base_wav, src_se=source_se, tgt_se=target_se, output_path=cloned_wav)
        
        # time stretching to match reference
        start_ms = time_to_ms(sub.start)
        target_ms = time_to_ms(sub.end) - time_to_ms(sub.start)
        stretched_wav = os.path.join(translated_dir, f"stretched_{i:04d}.wav")
        stretch_audio(cloned_wav, stretched_wav, target_ms)
        clip = AudioSegment.from_wav(stretched_wav)
        
        if i == 1:
            fr = clip.frame_rate
            ch = clip.channels
            sw = clip.sample_width
            timeline = AudioSegment.silent(duration=start_ms, frame_rate=fr).set_channels(ch).set_sample_width(sw)
            current_pos_ms = start_ms
        
        # adding to running_audio
        if start_ms > current_pos_ms:
            timeline += AudioSegment.silent(duration=start_ms - current_pos_ms, frame_rate=fr).set_channels(ch).set_sample_width(sw)
            current_pos_ms = start_ms
        
        clip = clip.set_frame_rate(fr).set_channels(ch).set_sample_width(sw)
        timeline += clip                 
        current_pos_ms += len(clip)      
    
        # clean up intermediate files (can comment out to see intermediates)
        os.remove(base_wav) # translated tts
        os.remove(cloned_wav) # cloned translation
        os.remove(stretched_wav) # stretched cloned translation

    # Export final audio
    timeline.export(final_wav, format="wav", parameters=["-acodec", "pcm_s16le", "-ar", str(fr), "-ac", str(ch)])

    print(f"Combined cloned audio saved to: {final_wav}")
    print(f"Duration: {len(timeline)/1000:.1f} seconds")


# copy video from original mp4 and audio from translation and overlay
def combine_audio_video(mp4_in, final_wav, mp4_out):
    subprocess.run(["ffmpeg", "-i", mp4_in, "-i", final_wav, "-map", "0:0", "-map", "1:0", '-c', "copy", mp4_out])

# configuration
mp4_in = "Tanzania-2.mp4"
srt_in = "Tanzania-caption.srt"

translated_srt = "translated.srt"
ckpt_converter = 'OpenVoice/checkpoints_v2/converter'
language = "german"
translated_dir = f"intermediate_{language}_outputs"
reference_voice = os.path.join(translated_dir, "reference_voice.wav")
final_wav = os.path.join(translated_dir, f"cloned_{language}_wav.wav")
mp4_out = "translated_vid.mp4"


new_audio(mp4_in, srt_in, language, reference_voice, translated_srt, final_wav)
combine_audio_video(mp4_in, final_wav, mp4_out)
