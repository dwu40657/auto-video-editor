"""Auto Video Editor - AI-powered video editing for Kuaishou"""

__version__ = "0.1.0"
__author__ = "dwu40657"

from src.main import VideoEditor
from src.video_analyzer import VideoAnalyzer
from src.subtitle_generator import SubtitleGenerator
from src.music_sync import MusicSynchronizer
from src.kuaishou_optimizer import KuaishouOptimizer

__all__ = [
    "VideoEditor",
    "VideoAnalyzer",
    "SubtitleGenerator",
    "MusicSynchronizer",
    "KuaishouOptimizer",
]
