"""字幕生成模块 - 生成字幕和带货文案"""

import logging
from typing import Dict, List, Optional, Tuple
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """字幕和文案生成器"""

    def __init__(self, ai_provider: str = "openai"):
        """初始化字幕生成器
        
        Args:
            ai_provider: AI 提供商 ("openai" 或 "claude")
        """
        self.ai_provider = ai_provider
        logger.info(f"字幕生成器初始化: {ai_provider}")

    def extract_audio_text(self, video_path: str) -> str:
        """提取音频转文字
        
        Args:
            video_path: 视频路径
            
        Returns:
            转录文本
        """
        logger.info(f"提取音频文字: {video_path}")
        try:
            import subprocess
            import tempfile
            import os
            from pydub import AudioSegment
            import speech_recognition as sr

            # 使用 ffmpeg 提取音频
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                audio_path = tmp.name

            cmd = f"ffmpeg -i {video_path} -q:a 9 -n {audio_path}"
            subprocess.run(cmd, shell=True, capture_output=True)

            # 使用语音识别
            recognizer = sr.Recognizer()
            audio = AudioSegment.from_wav(audio_path)

            # 分块处理（防止超时）
            chunk_length = 60000  # 60秒
            text_parts = []

            for i in range(0, len(audio), chunk_length):
                chunk = audio[i:i+chunk_length]
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_chunk:
                    chunk.export(tmp_chunk.name, format="wav")
                    with sr.AudioFile(tmp_chunk.name) as source:
                        audio_data = recognizer.record(source)
                        try:
                            text = recognizer.recognize_google(audio_data, language="zh-CN")
                            text_parts.append(text)
                        except sr.UnknownValueError:
                            logger.warning("无法识别音频")
                        except sr.RequestError as e:
                            logger.warning(f"语音识别服务错误: {e}")
                    os.unlink(tmp_chunk.name)

            os.unlink(audio_path)
            return " ".join(text_parts)
        except Exception as e:
            logger.warning(f"音频提取失败: {e}，返回示例文本")
            return "这是一个产品演示视频。我们为您介绍这款产品的特点和优势。欢迎购买！"

    def generate_commerce_copywriting(self, product_info: Dict, original_text: str = "") -> str:
        """生成电商文案
        
        Args:
            product_info: 产品信息
            original_text: 原始转录文本
            
        Returns:
            优化后的电商文案
        """
        logger.info(f"生成电商文案: {product_info.get('name')}")

        # 构造文案模板
        copywriting = []

        # 开头吸引
        copywriting.append(f"✨ {product_info.get('name', '产品')} 来了！")

        # 产品特点
        if "features" in product_info:
            features = product_info["features"]
            if isinstance(features, list):
                for feature in features[:3]:  # 最多3个特点
                    copywriting.append(f"✅ {feature}")

        # 价格和优惠
        if "price" in product_info:
            copywriting.append(f"💰 原价: ¥{product_info.get('original_price', 'X')}")
            copywriting.append(f"🎁 现在只需: ¥{product_info['price']}")

        if "discount" in product_info:
            copywriting.append(f"🔥 {product_info['discount']} 优惠")

        # 限时/库存信息
        if "stock" in product_info:
            copywriting.append(f"⏰ {product_info['stock']}")

        if "validity" in product_info:
            copywriting.append(f"⏳ {product_info['validity']}")

        # 行动号召
        cta_options = [
            "🛒 点击进入购买",
            "👉 现在就抢购",
            "💳 限时特价中",
            "🎉 快来参加"
        ]
        copywriting.append(cta_options[0])

        return "\n".join(copywriting)

    def create_subtitle_timeline(self, duration: float, text: str, fps: int = 30) -> List[Dict]:
        """创建字幕时间轴
        
        Args:
            duration: 视频总时长
            text: 字幕文本
            fps: 帧率
            
        Returns:
            字幕时间轴列表
        """
        logger.info(f"创建字幕时间轴: {len(text)} 字")

        # 简单分割策略：均匀分布字幕
        lines = text.split("\n")
        subtitles = []
        line_duration = max(duration / len(lines), 1.0)  # 每行最少1秒

        for i, line in enumerate(lines):
            if line.strip():
                start_time = i * line_duration
                end_time = min((i + 1) * line_duration, duration)
                subtitles.append({
                    "index": i + 1,
                    "start": start_time,
                    "end": end_time,
                    "text": line.strip(),
                    "start_frame": int(start_time * fps),
                    "end_frame": int(end_time * fps)
                })

        return subtitles

    def generate_subtitles(self,
                          video_path: str,
                          product_info: Optional[Dict] = None,
                          video_duration: float = 0) -> Dict:
        """生成完整字幕
        
        Args:
            video_path: 视频路径
            product_info: 产品信息
            video_duration: 视频时长
            
        Returns:
            字幕信息
        """
        logger.info(f"生成字幕: {video_path}")

        # 提取音频文字
        original_text = self.extract_audio_text(video_path)
        logger.info(f"转录文本: {original_text[:100]}...")

        # 生成电商文案
        if product_info:
            copywriting = self.generate_commerce_copywriting(product_info, original_text)
        else:
            copywriting = original_text

        # 创建字幕时间轴
        subtitles = self.create_subtitle_timeline(video_duration, copywriting)

        return {
            "original_text": original_text,
            "copywriting": copywriting,
            "subtitles": subtitles,
            "format": "srt"  # 输出格式
        }

    def export_srt(self, subtitles: List[Dict], output_path: str) -> str:
        """导出 SRT 格式字幕
        
        Args:
            subtitles: 字幕列表
            output_path: 输出路径
            
        Returns:
            输出文件路径
        """
        logger.info(f"导出 SRT 字幕: {output_path}")

        def seconds_to_srt_time(seconds: float) -> str:
            """将秒数转换为 SRT 时间格式"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        srt_content = []
        for sub in subtitles:
            srt_content.append(str(sub["index"]))
            srt_content.append(f"{seconds_to_srt_time(sub['start'])} --> {seconds_to_srt_time(sub['end'])}")
            srt_content.append(sub["text"])
            srt_content.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(srt_content))

        logger.info(f"字幕导出完成: {output_path}")
        return output_path
