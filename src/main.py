"""主程序 - 整合所有模块"""

import logging
import os
from typing import Dict, Optional
from pathlib import Path

from src.video_analyzer import VideoAnalyzer
from src.kuaishou_optimizer import KuaishouOptimizer
from src.subtitle_generator import SubtitleGenerator
from src.music_sync import MusicSynchronizer
from src.ai_processor import AIProcessor
from src.video_editor import VideoEditor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoEditingPipeline:
    """视频编辑流程管理"""

    def __init__(self,
                 video_path: str,
                 platform: str = "kuaishou",
                 ai_provider: str = "openai",
                 output_dir: str = "./outputs"):
        """初始化编辑流程
        
        Args:
            video_path: 输入视频路径
            platform: 平台 ("kuaishou", "douyin" 等)
            ai_provider: AI 提供商
            output_dir: 输出目录
        """
        self.video_path = video_path
        self.platform = platform
        self.ai_provider = ai_provider
        self.output_dir = output_dir

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 初始化各个模块
        self.analyzer = VideoAnalyzer(video_path)
        self.optimizer = KuaishouOptimizer() if platform == "kuaishou" else None
        self.subtitle_gen = SubtitleGenerator(ai_provider)
        self.music_sync = MusicSynchronizer()
        self.ai = AIProcessor(ai_provider)
        self.editor = VideoEditor(output_dir)

        logger.info(f"视频编辑流程初始化: {video_path} ({platform})")

    def analyze_video(self) -> Dict:
        """分析视频
        
        Returns:
            视频分析结果
        """
        logger.info("[步骤 1/6] 分析视频...")

        video_info = self.analyzer.get_video_info()
        scene_changes = self.analyzer.detect_scene_changes()
        highlights = self.analyzer.detect_highlights()
        tempo = self.analyzer.detect_tempo()
        transitions = self.analyzer.detect_transitions()

        analysis = {
            "video_info": video_info,
            "scene_changes": scene_changes,
            "highlights": highlights,
            "tempo": tempo,
            "transitions": transitions
        }

        logger.info(f"分析完成: 检测到 {len(highlights)} 个精彩片段")
        return analysis

    def optimize_for_platform(self, analysis: Dict) -> Dict:
        """针对平台优化
        
        Args:
            analysis: 视频分析结果
            
        Returns:
            优化方案
        """
        logger.info("[步骤 2/6] 针对平台优化...")

        if self.optimizer is None:
            logger.warning("未初始化平台优化器")
            return {}

        video_info = analysis["video_info"]
        highlights = analysis["highlights"]

        # 获取优化建议
        recommendations = self.optimizer.get_editing_recommendations(video_info, highlights)

        logger.info(f"优化方案生成完成")
        return recommendations

    def generate_subtitles(self, product_info: Optional[Dict] = None) -> Dict:
        """生成字幕
        
        Args:
            product_info: 产品信息（可选）
            
        Returns:
            字幕信息
        """
        logger.info("[步骤 3/6] 生成字幕...")

        video_duration = self.analyzer.duration
        subtitles_info = self.subtitle_gen.generate_subtitles(
            self.video_path,
            product_info,
            video_duration
        )

        # 导出 SRT 字幕
        srt_path = os.path.join(self.output_dir, "subtitles.srt")
        self.subtitle_gen.export_srt(subtitles_info["subtitles"], srt_path)

        logger.info(f"字幕生成完成: {srt_path}")
        return subtitles_info

    def prepare_music(self, music_library: Optional[list] = None) -> Dict:
        """准备背景音乐
        
        Args:
            music_library: 音乐库路径列表
            
        Returns:
            音乐同步方案
        """
        logger.info("[步骤 4/6] 准备背景音乐...")

        # 如果没有提供音乐库，使用默认的
        if not music_library:
            logger.warning("未提供音乐库，跳过音乐同步")
            return {}

        # 选择最佳音乐
        best_music = self.music_sync.find_best_music(music_library)
        logger.info(f"选择音乐: {best_music}")

        # 生成同步计划
        video_info = self.analyzer.get_video_info()
        sync_plan = self.music_sync.generate_sync_plan(video_info, best_music)

        logger.info(f"音乐同步计划生成完成")
        return sync_plan

    def predict_performance(self, analysis: Dict) -> Dict:
        """预测视频效果
        
        Args:
            analysis: 视频分析结果
            
        Returns:
            效果预测
        """
        logger.info("[步骤 5/6] 预测视频效果...")

        prediction = self.ai.predict_conversion_rate(analysis)
        logger.info(f"预测转化率: {prediction['conversion_rate']:.1f}%")
        return prediction

    def process(self,
                product_info: Optional[Dict] = None,
                music_library: Optional[list] = None) -> Dict:
        """完整处理流程
        
        Args:
            product_info: 产品信息（用于生成文案）
            music_library: 音乐库列表
            
        Returns:
            处理结果
        """
        logger.info("="*60)
        logger.info("开始视频编辑流程")
        logger.info("="*60)

        try:
            # 步骤 1: 分析视频
            analysis = self.analyze_video()

            # 步骤 2: 平台优化
            optimization = self.optimize_for_platform(analysis)

            # 步骤 3: 生成字幕
            subtitles = self.generate_subtitles(product_info)

            # 步骤 4: 准备音乐
            music_plan = self.prepare_music(music_library)

            # 步骤 5: 预测效果
            prediction = self.predict_performance(analysis)

            # 步骤 6: 生成最终报告
            logger.info("[步骤 6/6] 生成最终报告...")

            result = {
                "status": "success",
                "output_dir": self.output_dir,
                "analysis": analysis,
                "optimization": optimization,
                "subtitles": subtitles,
                "music_plan": music_plan,
                "prediction": prediction,
                "summary": {
                    "video_path": self.video_path,
                    "platform": self.platform,
                    "duration": analysis["video_info"].get("duration", 0),
                    "conversion_prediction": prediction.get("conversion_rate", 0),
                    "highlights_count": len(analysis["highlights"]),
                    "recommended_duration": optimization.get("duration_optimization", {}).get("target_duration", 0)
                }
            }

            logger.info("="*60)
            logger.info("视频编辑流程完成！")
            logger.info(f"预测转化率: {prediction.get('conversion_rate', 0):.1f}%")
            logger.info(f"输出目录: {self.output_dir}")
            logger.info("="*60)

            return result

        except Exception as e:
            logger.error(f"视频编辑流程失败: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }


class VideoEditor:
    """用户友好的视频编辑器接口"""

    def __init__(self,
                 video_path: str,
                 platform: str = "kuaishou",
                 ai_provider: str = "openai",
                 output_dir: str = "./outputs"):
        """初始化视频编辑器
        
        Args:
            video_path: 视频路径
            platform: 目标平台
            ai_provider: AI 提供商
            output_dir: 输出目录
        """
        self.pipeline = VideoEditingPipeline(
            video_path, platform, ai_provider, output_dir
        )

    def process(self,
                product_info: Optional[Dict] = None,
                music_library: Optional[list] = None) -> Dict:
        """处理视频
        
        Args:
            product_info: 产品信息
            music_library: 音乐库
            
        Returns:
            处理结果
        """
        return self.pipeline.process(product_info, music_library)


if __name__ == "__main__":
    # 示例使用
    logger.info("视频编辑工具启动")

    # 测试产品信息
    test_product = {
        "name": "爆款面膜",
        "price": "99.9",
        "original_price": "199.9",
        "discount": "5折",
        "features": ["深层补水", "美白淡斑", "抗衰老"],
        "stock": "仅剩50份",
        "validity": "今日限时"
    }

    # 这里可以添加实际的视频处理代码
    logger.info("示例配置完成")
