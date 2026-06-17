"""视频分析模块 - 检测精彩片段、节奏、转场点"""

import cv2
import numpy as np
import librosa
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """视频分析器 - 分析视频内容、节奏、转场等"""

    def __init__(self, video_path: str):
        """初始化视频分析器
        
        Args:
            video_path: 视频文件路径
        """
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0
        logger.info(f"视频加载: {video_path}, 时长: {self.duration:.2f}s, FPS: {self.fps}")

    def detect_scene_changes(self, threshold: float = 20.0) -> List[Dict]:
        """检测场景转换点
        
        Args:
            threshold: 转换检测阈值 (0-100)
            
        Returns:
            场景转换列表，包含时间戳和置信度
        """
        logger.info("检测场景转换...")
        scene_changes = []
        prev_frame = None
        frame_index = 0

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # 缩小帧大小以加快处理
            frame_resized = cv2.resize(frame, (320, 240))
            gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                # 计算帧差
                diff = cv2.absdiff(prev_frame, gray)
                mean_diff = np.mean(diff)

                if mean_diff > threshold:
                    timestamp = frame_index / self.fps
                    confidence = min(mean_diff / 100.0, 1.0)
                    scene_changes.append({
                        "timestamp": timestamp,
                        "frame_index": frame_index,
                        "confidence": confidence
                    })

            prev_frame = gray
            frame_index += 1

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 重置到开始
        logger.info(f"检测到 {len(scene_changes)} 个场景转换")
        return scene_changes

    def detect_highlights(self, sensitivity: float = 0.7) -> List[Dict]:
        """检测精彩片段（高动作、高对比度）
        
        Args:
            sensitivity: 灵敏度 (0.1-1.0)
            
        Returns:
            精彩片段列表
        """
        logger.info("检测精彩片段...")
        highlights = []
        window_size = int(self.fps * 2)  # 2秒窗口
        motion_scores = []
        frame_index = 0

        prev_frame = None
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame_resized = cv2.resize(frame, (320, 240))
            gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                flow = cv2.calcOpticalFlowFarneback(
                    prev_frame, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
                )
                motion = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2).mean()
                motion_scores.append(motion)
            else:
                motion_scores.append(0)

            prev_frame = gray
            frame_index += 1

        # 找到高动作区间
        threshold = np.percentile(motion_scores, 100 - sensitivity * 100)
        in_highlight = False
        start_time = 0

        for i, score in enumerate(motion_scores):
            timestamp = i / self.fps
            if score > threshold and not in_highlight:
                start_time = timestamp
                in_highlight = True
            elif score <= threshold and in_highlight:
                highlights.append({
                    "start": start_time,
                    "end": timestamp,
                    "duration": timestamp - start_time,
                    "score": float(score)
                })
                in_highlight = False

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 重置到开始
        logger.info(f"检测到 {len(highlights)} 个精彩片段")
        return highlights

    def extract_audio(self) -> Tuple[np.ndarray, int]:
        """提取视频音频
        
        Returns:
            音频数据和采样率
        """
        logger.info("提取音频...")
        # 这里需要使用 ffmpeg 或 moviepy
        # 为了简化，返回空的音频数据
        try:
            import subprocess
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            # 使用 ffmpeg 提取音频
            cmd = f"ffmpeg -i {self.video_path} -q:a 9 -n {tmp_path}"
            subprocess.run(cmd, shell=True, capture_output=True)

            # 使用 librosa 加载音频
            y, sr = librosa.load(tmp_path, sr=None)
            os.unlink(tmp_path)

            logger.info(f"音频提取完成: {sr}Hz")
            return y, sr
        except Exception as e:
            logger.warning(f"音频提取失败: {e}, 返回空音频")
            return np.array([]), 44100

    def detect_tempo(self) -> Dict:
        """检测音乐节奏/BPM
        
        Returns:
            包含 BPM 和节拍帧的字典
        """
        logger.info("检测音乐节奏...")
        y, sr = self.extract_audio()

        if len(y) == 0:
            logger.warning("无法提取音频，返回默认 BPM")
            return {"bpm": 120, "beat_frames": [], "confidence": 0.0}

        try:
            # 计算节奏
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            bpm = librosa.feature.tempo(y=y, sr=sr)[0]
            beats, _ = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr)
            beat_frames = (beat_times * self.fps).astype(int)

            logger.info(f"检测到 BPM: {bpm:.1f}")
            return {
                "bpm": float(bpm),
                "beat_frames": beat_frames.tolist(),
                "confidence": 0.8
            }
        except Exception as e:
            logger.warning(f"BPM 检测失败: {e}")
            return {"bpm": 120, "beat_frames": [], "confidence": 0.0}

    def detect_transitions(self) -> List[Dict]:
        """检测转场点
        
        Returns:
            转场点列表
        """
        logger.info("检测转场点...")
        # 转场点通常是场景变化最大的地方
        scene_changes = self.detect_scene_changes(threshold=25.0)
        transitions = [sc for sc in scene_changes if sc["confidence"] > 0.6]

        logger.info(f"检测到 {len(transitions)} 个转场")
        return transitions

    def get_video_info(self) -> Dict:
        """获取视频信息
        
        Returns:
            视频信息字典
        """
        return {
            "path": self.video_path,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "duration": self.duration,
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        }

    def close(self):
        """关闭视频捕获"""
        if self.cap:
            self.cap.release()
