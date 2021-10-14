from enum import Enum
from typing import NamedTuple


class SupportedLinks(Enum):
    SOUNDCLOUD = "soundcloud.com"
    SOUNDCLOUD_GOOGLE = "soundcloud.app.goo.gl"
    DROPBOX = "dropbox.com"


class SupportedFormats(Enum):
    MP3 = ".mp3"
    MP4A = ".mp4a"
    WAV = ".wav"
    FLAC = ".flac"


class MessageResponseContext(NamedTuple):
    author: str
    content: str
    jump_url: str
    author_id: str
    message_id: str
