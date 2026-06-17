"""音乐同步模块 - 检测节奏并同步背景音乐"""

import logging
from typing import Dict, List, Optional
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MusicSynchronizer:
    """音乐同步器 - 管理背景音乐和节奏同步"""

    def __init__(self):
        """初始化音乐同步器"""
        # 快手推荐的音乐 BPM 范围
        self.recommended_bpm_range = (100, 140)
        logger.info("音乐同步器初始化完成")

    def analyze_music_tempo(self, music_path: str) -> Dict:
        """分析音乐的节奏/BPM
        
        Args:
            music_path: 音乐文件路径
            
        Returns:
            音乐节奏分析结果
        """
        logger.info(f"分析音乐节奏: {music_path}")
        try:
            import librosa
            y, sr = librosa.load(music_path, sr=None)
            bpm = librosa.feature.tempo(y=y, sr=sr)[0]
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onset_frames = librosa.util.peak_pick(onset_env, pre_max=3, post_max=3, pre_avg=3, post_avg=3, delta=0.1, wait=10)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)

            logger.info(f"音乐 BPM: {bpm:.1f}")
            return {
                "path": music_path,
                "bpm": float(bpm),
                "onset_times": onset_times.tolist(),
                "duration": float(librosa.get_duration(y=y, sr=sr))
            }
        except Exception as e:
            logger.warning(f"音乐分析失败: {e}")
            return {
                "path": music_path,
                "bpm": 120,  # 默认 BPM
                "onset_times": [],
                "duration": 0
            }

    def find_best_music(self, music_library: List[str], target_bpm: Optional[float] = None) -> str:
        """从音乐库中找到最佳背景音乐
        
        Args:
            music_library: 音乐文件路径列表
            target_bpm: 目标 BPM（如果为 None，则在推荐范围内选择）
            
        Returns:
            最佳音乐文件路径
        """
        logger.info(f"从 {len(music_library)} 首音乐中选择...")

        if not music_library:
            logger.warning("音乐库为空")
            return ""

        if target_bpm is None:
            target_bpm = np.mean(self.recommended_bpm_range)

        best_music = music_library[0]
        best_score = float('inf')

        for music_path in music_library:
            analysis = self.analyze_music_tempo(music_path)
            bpm = analysis["bpm"]

            # 计算与目标 BPM 的距离
            bpm_diff = abs(bpm - target_bpm)

            # 惩罚推荐范围外的 BPM
            if bpm < self.recommended_bpm_range[0] or bpm > self.recommended_bpm_range[1]:
                bpm_diff *= 1.5

            if bpm_diff < best_score:
                best_score = bpm_diff
                best_music = music_path

        logger.info(f"选中音乐: {best_music}")
        return best_music

    def sync_music_to_video(self,
                           video_tempo: float,
                           music_path: str,
                           video_duration: float) -> Dict:
        """同步音乐到视频
        
        Args:
            video_tempo: 视频节奏 (BPM)
            music_path: 音乐文件路径
            video_duration: 视频时长
            
        Returns:
            同步方案
        """
        logger.info(f"同步音乐: {music_path} (视频 BPM: {video_tempo})")

        music_info = self.analyze_music_tempo(music_path)
        music_bpm = music_info["bpm"]
        music_duration = music_info["duration"]

        # 计算速度倍数
        speed_ratio = video_tempo / music_bpm if music_bpm > 0 else 1.0

        # 如果倍数偏离过大，使用循环播放而不是变速
        if speed_ratio < 0.8 or speed_ratio > 1.2:
            logger.info(f"速度倍数过大 ({speed_ratio:.2f}x)，使用循环播放")
            loops_needed = video_duration / music_duration if music_duration > 0 else 1
            return {
                "method": "loop",
                "music_path": music_path,
                "speed_ratio": 1.0,
                "loops": int(loops_needed) + 1,
                "trim_duration": video_duration
            }
        else:
            logger.info(f"使用变速: {speed_ratio:.2f}x")
            return {
                "method": "speed_adjust",
                "music_path": music_path,
                "speed_ratio": float(speed_ratio),
                "original_bpm": float(music_bpm),
                "target_bpm": float(video_tempo),
                "trim_duration": video_duration
            }

    def generate_sync_plan(self, video_info: Dict, music_path: str) -> Dict:
        """生成完整的音乐同步计划
        
        Args:
            video_info: 视频信息
            music_path: 音乐路径
            
        Returns:
            同步计划
        """
        logger.info("生成音乐同步计划...")

        video_tempo = video_info.get("tempo", 120)  # 如果没有检测到，使用默认值
        video_duration = video_info.get("duration", 0)

        sync_plan = self.sync_music_to_video(video_tempo, music_path, video_duration)

        sync_plan["recommendations"] = [
            "✅ 音乐应该在开头 0.5 秒淡入",
            "✅ 音乐应该在结尾 0.5 秒淡出",
            "✅ 音乐音量应该在 -6dB 到 -10dB（相对于主音声）",
            "✅ 避免音乐和旁白重叠过多",
        ]

        return sync_plan

    def get_recommended_bpm(self) -> tuple:
        """获取快手推荐的 BPM 范围
        
        Returns:
            (最小 BPM, 最大 BPM)
        """
        return self.recommended_bpm_range
