import datetime
import io
import os

from discord import VoiceClient
from discord.sinks import Filters, default_filters, AudioData, Sink
from discord.types import snowflake


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

    def init(self, vc):  # called under listen
        self.vc: VoiceClient = vc
        super().init(vc)

    @Filters.container
    def write(self, data, user):
        if user not in self.audio_data:
            file = io.BytesIO()
            self.audio_data.update({user: AudioData(file)})

        file = self.audio_data[user]
        file.write(data)

        print(f'Time: {datetime.datetime.now()} -- size: {len(data)}')

    def cleanup(self):
        self.finished = True
        for file in self.audio_data.values():
            file.cleanup()

    def get_all_audio(self):
        """Gets all audio files."""
        return [x.file for x in self.audio_data.values()]

    def get_user_audio(self, user: snowflake.Snowflake):
        """Gets the audio file(s) of one specific user."""
        return os.path.realpath(self.audio_data.pop(user))
