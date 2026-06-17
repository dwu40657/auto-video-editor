"""快手优化模块 - 专为快手平台优化视频"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KuaishouOptimizer:
    """快手视频优化器"""

    # 快手平台规格
    KUAISHOU_SPECS = {
        "aspect_ratio": "9:16",
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "codec": "h264",
        "optimal_duration_min": 15,
        "optimal_duration_max": 60,
        "optimal_duration_target": 30,
        "bitrate": "5-8M",
        "audio_sample_rate": 48000,
    }

    def __init__(self, config_path: Optional[str] = None):
        """初始化快手优化器
        
        Args:
            config_path: 配置文件路径
        """
        self.specs = self.KUAISHOU_SPECS.copy()
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
                self.specs.update(custom_config.get('kuaishou', {}))
        logger.info("快手优化器初始化完成")

    def check_video_format(self, video_info: Dict) -> Dict:
        """检查视频格式是否符合快手规范
        
        Args:
            video_info: 视频信息
            
        Returns:
            检查结果和建议
        """
        logger.info("检查视频格式...")
        issues = []
        suggestions = []

        # 检查分辨率
        if video_info.get("width") != self.specs["width"] or \
           video_info.get("height") != self.specs["height"]:
            issues.append(f"分辨率不符: {video_info.get('width')}x{video_info.get('height')}")
            suggestions.append(f"需要缩放至 {self.specs['width']}x{self.specs['height']}")

        # 检查 FPS
        if abs(video_info.get("fps", 0) - self.specs["fps"]) > 1:
            issues.append(f"帧率不符: {video_info.get('fps')}")
            suggestions.append(f"需要转换至 {self.specs['fps']} FPS")

        # 检查时长
        duration = video_info.get("duration", 0)
        if duration < self.specs["optimal_duration_min"]:
            suggestions.append(f"视频时长过短 ({duration:.1f}s), 建议至少 {self.specs['optimal_duration_min']}s")
        elif duration > self.specs["optimal_duration_max"]:
            issues.append(f"视频时长过长 ({duration:.1f}s), 需要裁剪到 {self.specs['optimal_duration_max']}s 以内")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }

    def optimize_duration(self, duration: float, highlights: List[Dict]) -> Dict:
        """优化视频时长
        
        Args:
            duration: 原始时长
            highlights: 精彩片段列表
            
        Returns:
            优化方案
        """
        logger.info(f"优化视频时长: {duration:.2f}s")

        target_duration = self.specs["optimal_duration_target"]
        max_duration = self.specs["optimal_duration_max"]

        if duration <= target_duration:
            return {
                "action": "keep",
                "target_duration": duration,
                "reason": "时长已在最优范围内"
            }

        if duration <= max_duration:
            return {
                "action": "slight_cut",
                "target_duration": min(duration, target_duration),
                "reason": f"建议剪辑至 {target_duration}s 以提高转化率"
            }

        # 需要大幅剪辑
        # 优先保留精彩片段
        total_highlight_duration = sum(h["duration"] for h in highlights)

        if total_highlight_duration >= target_duration:
            return {
                "action": "aggressive_cut",
                "target_duration": target_duration,
                "reason": f"视频过长，使用精彩片段组合至 {target_duration}s",
                "use_highlights_only": True
            }

        return {
            "action": "aggressive_cut",
            "target_duration": max_duration,
            "reason": f"视频过长，剪辑至最大允许时长 {max_duration}s"
        }

    def optimize_aspect_ratio(self, width: int, height: int) -> Dict:
        """优化宽高比
        
        Args:
            width: 原始宽度
            height: 原始高度
            
        Returns:
            裁剪方案
        """
        target_ratio = 9 / 16
        current_ratio = width / height if height > 0 else 0

        logger.info(f"当前比例: {current_ratio:.3f}, 目标比例: {target_ratio:.3f}")

        if abs(current_ratio - target_ratio) < 0.01:
            return {
                "action": "none",
                "reason": "宽高比已符合"
            }

        if current_ratio > target_ratio:
            # 宽度过大，需要左右裁剪
            new_width = int(height * target_ratio)
            crop_x = (width - new_width) // 2
            return {
                "action": "crop_horizontal",
                "x": crop_x,
                "y": 0,
                "width": new_width,
                "height": height,
                "reason": "宽度过大，进行左右裁剪"
            }
        else:
            # 高度过大，需要上下裁剪
            new_height = int(width / target_ratio)
            crop_y = (height - new_height) // 2
            return {
                "action": "crop_vertical",
                "x": 0,
                "y": crop_y,
                "width": width,
                "height": new_height,
                "reason": "高度过大，进行上下裁剪"
            }

    def optimize_text_placement(self, highlights: List[Dict]) -> Dict:
        """优化文字位置（字幕和文案）
        
        Args:
            highlights: 精彩片段列表
            
        Returns:
            文字位置优化方案
        """
        logger.info("优化文字位置...")

        return {
            "title_position": "top_center",  # 标题放在上方
            "title_safe_area": {"x": 0.1, "y": 0.05, "width": 0.8, "height": 0.15},
            "subtitle_position": "bottom_center",  # 字幕放在下方
            "subtitle_safe_area": {"x": 0.1, "y": 0.75, "width": 0.8, "height": 0.2},
            "cta_position": "center",  # CTA (行动号召) 放在中心
            "cta_safe_area": {"x": 0.2, "y": 0.4, "width": 0.6, "height": 0.2},
            "recommendations": [
                "标题/价格信息应在前 3 秒显示",
                "CTA 文案应频繁出现",
                "产品名称和价格应突出显示"
            ]
        }

    def get_editing_recommendations(self, video_info: Dict, highlights: List[Dict]) -> Dict:
        """获取编辑建议
        
        Args:
            video_info: 视频信息
            highlights: 精彩片段列表
            
        Returns:
            编辑建议
        """
        logger.info("生成编辑建议...")

        recommendations = {
            "format_check": self.check_video_format(video_info),
            "duration_optimization": self.optimize_duration(video_info["duration"], highlights),
            "aspect_ratio": self.optimize_aspect_ratio(video_info["width"], video_info["height"]),
            "text_placement": self.optimize_text_placement(highlights),
            "best_practices": [
                "✅ 开头 3 秒立即展示产品或吸引眼球",
                "✅ 保持快速剪辑节奏（平均镜头 2-3 秒）",
                "✅ 突出价格、折扣、限时信息",
                "✅ 使用高对比度字体和颜色",
                "✅ 配乐 BPM 建议 120-140",
                "✅ 真人出镜增加信任度",
                "✅ 展示使用场景和用户评价",
                "✅ 强化 CTA (点击购买/现在抢购)",
            ]
        }

        return recommendations

    def get_kuaishou_specs(self) -> Dict:
        """获取快手平台规格
        
        Returns:
            快手平台规格
        """
        return self.specs.copy()
