import asyncio
import datetime
import io
import os
from queue import Queue
import threading

from discord.opus import Decoder as OpusDecoder

from discord import VoiceClient
from discord.sinks import Filters, default_filters, Sink
from pydub import AudioSegment
from discord.types import snowflake
import openai


class MyPcmSink(Sink):
    """A sink "stores" recorded audio data.

    Can be subclassed for extra customizablilty.

    .. warning::
        It is recommended you use
        the officially provided sink classes,
        such as :class:`~discord.sinks.WaveSink`.

    just replace the following like so: ::

        vc.start_recording(
            MySubClassedSink(),
            finished_callback,
            ctx.channel,
        )

    .. versionadded:: 2.0

    Raises
    ------
    ClientException
        An invalid encoding type was specified.
    ClientException
        Audio may only be formatted after recording is finished.
    """

    def __init__(self, *, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)
        self.encoding = "pcm"
        self.vc = None
        self.audio_data = {}
        self.trunk = io.BytesIO()
        self.trunk_lock = threading.Lock()
        self.processing_thread = None
        self.trunk_duration = 3
        self.sample_width = OpusDecoder.SAMPLE_SIZE // OpusDecoder.CHANNELS
        self.channels = OpusDecoder.CHANNELS
        self.frame_rate = OpusDecoder.SAMPLING_RATE
        self.bytes_per_frame = self.sample_width * self.channels
        self.trunk_size = self.trunk_duration * self.frame_rate * self.bytes_per_frame
        self.openai_client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))
        self.processing_queue = Queue()
        self.is_running = True
        self.start_processing_thread()
        

    def init(self, vc):  # called under listen
        self.vc: VoiceClient = vc
        super().init(vc)

    def start_processing_thread(self):
        self.processing_thread = threading.Thread(target=self.process_queue)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    @Filters.container
    def write(self, data, user):
        # print(f'Time: {datetime.datetime.now()} -- size: {len(data)}')
        # if user not in self.audio_data:
        #     file = io.BytesIO()
        #     self.audio_data.update({user: AudioData(file)})

        # file = self.audio_data[user]
        # file.write(data)

        with self.trunk_lock:
            self.trunk.write(data)
            if self.trunk.tell() >= self.trunk_size:
                audio_data = self.trunk.getvalue()
                self.trunk = io.BytesIO()  # Reset trunk
                self.processing_queue.put((audio_data, user))                


    def process_queue(self):
        while self.is_running:
            try:
                audio_data, user = self.processing_queue.get()
                self.process_trunk(audio_data, user)
                self.processing_queue.task_done()
            except Queue.empty:
                continue
            

    def process_trunk(self, audio_data, user):
        try:
            print(f"Processing audio for user {user}")
            audio = AudioSegment(
                data=audio_data,
                sample_width=self.sample_width,
                channels=self.channels,
                frame_rate=self.frame_rate
            )

            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)

            transcription = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=("trunk.wav",wav_io),
                response_format="verbose_json"
            )

            is_recognized = not all([segment["no_speech_prob"] > 0.6 or segment["avg_logprob"] < -1.5 for segment in transcription.segments])

            if not is_recognized:
                transcription.text = ""

            

            print(f"User {user}: {transcription.text}")
            
        except Exception as e:
            print(f"Error in OpenAI API call: {e}")



    # def cleanup(self):
    #     self.finished = True
    #     for file in self.audio_data.values():
    #         file.cleanup()

    def cleanup(self):
        with self.trunk_lock:
            if self.trunk.tell() > 0:
                audio_data = self.trunk.getvalue()
                self.processing_queue.put((audio_data, None))

        self.is_running = False

        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=10)  # Wait for up to 10 seconds
            if self.processing_thread.is_alive():
                print("Warning: Processing thread did not terminate within the timeout period.")

        self.processing_queue.join()
        self.trunk.close()
        print("Cleanup complete.")

    def get_all_audio(self):
        """Gets all audio files."""
        return [x.file for x in self.audio_data.values()]

    def get_user_audio(self, user: snowflake.Snowflake):
        """Gets the audio file(s) of one specific user."""
        return os.path.realpath(self.audio_data.pop(user))
    
