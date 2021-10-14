from enum import Enum


class SupportedLinks(Enum):
    SOUNDCLOUD = "soundcloud.com"
    SOUNDCLOUD_GOOGLE = "soundcloud.app.goo.gl"
    DROPBOX = "dropbox.com"


class SupportedFormats(Enum):
    MP3 = ".mp3"
    MP4A = ".mp4a"
    WAV = ".wav"
    FLAC = ".flac"
