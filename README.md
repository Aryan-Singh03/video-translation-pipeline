# Video Translation and Cloning Pipeline

This repository implements a complete video translation pipeline that converts English videos to a language of the user's choice while preserving the original speaker's voice characteristics, tone, and identity.

## Overview

Given an input MP4 video and corresponding SRT subtitle file, this pipeline:
1. Extracts original audio and translates subtitles to intended language
2. Generates new language speech using Google TTS
3. Applies voice cloning using OpenVoice to match the original speaker's characteristics
4. Synchronizes the cloned audio with video timing
5. Produces a final translated video with seamless audio replacement

## Requirements

- **Python 3.9** (required for compatibility with all dependencies)
- Sufficient disk space for model downloads (~1GB for OpenVoice model and checkpoint)
- Input files: MP4 video and corresponding SRT subtitle file

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3.9 -m venv venv
   source venv/bin/activate  # windows: venv\Scripts\activate
   ```

3. **Install dependencies and download models:**
   ```bash
   python setup.py
   ```
   
   This will download everything from requirements.txt as well as OpenVoice model and checkpoint files needed for voice cloning.

## Usage

1. **Prepare your input files:**
   - Place your MP4 video file and corresponding SRT file in the project directory
   - Ensure the SRT file contains English subtitles with proper timing

2. **Configure the translation:**
   - Open `translate.py` (or `demo.py`)
   - Modify the following parameters:
     ```python
     mp4_in = "your_video.mp4"
     srt_in = "your_subtitles.srt"
     target_language = "de"  # German
     ```

3. **Run the translation:**
   ```bash
   python translate.py
   ```

## Example Usage

An example input and output are provided in the `example/` folder:
- `example/input.mp4` - Sample English video
- `example/input.srt` - Corresponding English subtitles
- `example/output.mp4` - Translated  video
- `example/intermediates/` - Processing intermediates for debugging

To test with the example:
```bash
python translate.py  # Using example files as default
```

## Pipeline Steps

1. **Audio Extraction:** Separates audio from the input video
2. **Translation:** Converts SRT subtitles from English to German using translation services
3. **TTS Generation:** Creates German speech using Google Text-to-Speech
4. **Voice Analysis:** Analyzes original audio for sentiment and voice characteristics
5. **Voice Cloning:** Applies OpenVoice model to transfer original speaker's voice to German audio
6. **Audio Synchronization:** Stretches/aligns cloned audio segments to match original timing
7. **Video Assembly:** Combines translated audio with original video (audio removed)

## Output Files

The pipeline generates:
- **Final translated video:** `output.mp4` with German audio
- **Intermediate files** (for debugging):
  - `extracted_audio.wav` - Original audio track
  - `translated_tts.wav` - Raw German TTS audio
  - `cloned_audio.wav` - Voice-cloned German audio
  - `translated_subtitles.srt` - German subtitle file

## Limitations and Assumptions

### Current Limitations:
1. **Dependency Management:** Requires multiple libraries with specific versions - future deprecations could cause issues
2. **Memory Intensive:** Downloads and stores large model files locally (~1GB)
3. **Processing Efficiency:** Calls voice cloning model for each subtitle segment individually rather than batch processing
4. **Manual SRT Requirement:** Requires pre-existing subtitle files

### Assumptions:
- Input video has clear, single-speaker audio
- SRT file accurately represents the audio timing
- Sufficient system resources for model inference

## Future Enhancements

1. **Lip Syncing:** Implement lip syncing for better video quality
2. **Automatic Subtitle Extraction:** Implement speech-to-text to generate SRT files automatically
3. **Alternative Voice Cloning Models:** Explore ElevenLabs, Coqui, or other voice cloning services
4. **Batch Processing:** Optimize model calls for better performance on longer videos instead of calling per subtitle
5. **Direct Generation:** Skip TTS intermediate step and generate voice-cloned audio directly
6. **LLM Comparison:** Compare performance with large language model approaches (e.g., OpenAI)

## Dependencies

See `requirements.txt` for complete dependency list. Key libraries include:
- OpenVoice (voice cloning)
- Google Text-to-Speech
- Various audio processing libraries

## Troubleshooting

- **Python Version:** Ensure you're using Python 3.9 for compatibility
- **Model Download:** If setup fails, check internet connection and disk space
- **Audio Quality:** For best results, use videos with clear, single-speaker audio
- **Memory Issues:** Close other applications if experiencing memory constraints during processing

## Contributing

Feel free to submit issues and enhancement requests. Contributions are welcome!

## License

MIT
