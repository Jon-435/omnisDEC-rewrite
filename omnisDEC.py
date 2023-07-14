import datetime
from subprocess import Popen, PIPE
from threading import Event, Thread
import time
from EASGen import EASGen
from pydub import AudioSegment
from EAS2Text import EAS2Text
from numpy import frombuffer, int16
import pyaudio
import wave
from pydub.playback import play

# Modify the callsign to your liking. It MUST be 8 characters long without any dashes, underscores, or non ASCII characters.
callsign = "WINDOWS7"

def record(filename):
    try:
        ffmpeg_cmd = [
            "ffmpeg.exe",
            "-loglevel",
            "verbose",
            "-y",  # Overwrite output file if it exists
            "-f",
            "s16le",
            "-ar",
            "24000",
            "-ac",
            "1",
            "-i",
            "pipe:0",
            "-c:a",
            "pcm_s16le",
            filename
        ]
        # Open an instance of FFMPEG to write pcm_s16le data to a WAV file
        ffmpeg_record = Popen(ffmpeg_cmd, stdin=PIPE, stderr=PIPE)  # Pass audio_stream directly to Popen

        # Start a separate thread to read and pipe the audio data
        while True:
            data = audio_stream.stdout.read(4000)
            ffmpeg_record.stdin.write(data)  # Write data to ffmpeg process
            if recording == False:
                ffmpeg_record.terminate() #Terminate ffmpeg_cmd
                break

    except Exception as e:
        print("A Recording Error Has Occurred! Error: ", e)


def encode(header, filename):
    encoding = True
    eas_header = header
    header_segments = eas_header.split("-")
    header_segments[-2] = callsign
    new_eas_header = "-".join(header_segments)
    print("Alert Encoded! Sending alert with SAME header of:", new_eas_header)
    #send_to_discord(self.url, new_eas_header, True)

    alertAudio = AudioSegment.from_wav(filename)  # Import Audio data
    Alert = EASGen.genEAS(
        header=new_eas_header,
        attentionTone=False,
        audio=alertAudio,
        mode="DIGITAL",
        endOfMessage=True,
        sampleRate=32000,
    )  # Generate an EAS SAME message with an ATTN signal, the imported WAV file as the audio, with EOMs, and with a SAGE DIGITAL ENDEC style.
    play(Alert)
    print("\nAlert Sent! Returning to monitoring for alerts.")


def endec(url, num):
    print("Initializing Monitor ", num)
    global audio_stream
    global recording
    global same_stream
    global same_header
    global encoding

    # The decoder
    while True:
        monitor_cmd = [
            "ffmpeg.exe",
            "-hide_banner",
            "-nostdin",
            "-loglevel",
            "quiet",
            "-nostats",
            "-i",
            url,
            "-f",
            "s16le",
            "-c:a",
            "pcm_s16le",
            "-ar",
            "24000",
            "-ac",
            "1",
            "-"
        ]
        audio_stream = Popen(monitor_cmd, stdout=PIPE, stderr=PIPE)
        alert_stream = Popen(["decoder.exe", "-r", "24000"], stdin=audio_stream.stdout, stdout=PIPE, stderr=PIPE)

        while True:
            line = alert_stream.stdout.readline().decode("utf-8").strip("\n")
            data = audio_stream.stdout.read(4000)
            samples = frombuffer(data, dtype=int16)
            try:
                alert_stream.stdin.write(samples.tobytes())  # Convert samples to bytes and write to stdin
            except Exception as e:
                print(f"Monitor {num} ERROR: ", e)

            if "ZCZC" in line:
                recording = True
                same_header = line
                filename = f"alert_audio_mon{num}.wav"
                print(f"SAME Alert Received on Monitor {num}! SAME Header is {same_header}! Alert will now be recorded!")

                # Start the recording thread if it's not already running
                record_thread = Thread(target=record, args=(filename,))
                record_thread.start()

            elif "NNNN" in line:
                print("EOM Detected on Monitor", num, "! Stopping recording")
                recording = False
                print(f"[MONITOR {num}] Alert recorded! Modifying audio...")

                audio = AudioSegment.from_wav(filename)
                # Adjust the audio to be divisible by 16 and 24000
                samples = audio.get_array_of_samples()
                frames = len(samples) // audio.channels
                frames -= frames % (16 * 24000)  # Adjust the frames to be divisible
                samples = samples[:frames * audio.channels]
                audio = audio._spawn(samples)
                # Set the frame rate, channels, and sample width
                audio = audio.set_frame_rate(24000).set_channels(1).set_sample_width(2)
                # Save the modified audio
                audio.export(filename, format="wav")
                print(f"[MONITOR {num}] Alert modified! Encoding alert!")
                encode(same_header, filename)


# Modify the following variables according to your code
num = 1
url = "http://radiorandom.org:8000/test"
wait_event = Event()
endec(url, num)