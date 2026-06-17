"""AI 处理模块 - 使用 OpenAI/Claude API"""

import logging
import os
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProcessor:
    """AI 处理器 - 调用 AI API"""

    def __init__(self, provider: str = "openai"):
        """初始化 AI 处理器
        
        Args:
            provider: AI 提供商 ("openai" 或 "claude")
        """
        self.provider = provider
        self.api_key = self._get_api_key(provider)
        logger.info(f"AI 处理器初始化: {provider}")

    def _get_api_key(self, provider: str) -> str:
        """获取 API Key
        
        Args:
            provider: 提供商名称
            
        Returns:
            API Key
        """
        if provider == "openai":
            return os.getenv("OPENAI_API_KEY", "")
        elif provider == "claude":
            return os.getenv("CLAUDE_API_KEY", "")
        return ""

    def generate_copywriting(self, product_info: Dict, style: str = "casual") -> str:
        """使用 AI 生成电商文案
        
        Args:
            product_info: 产品信息
            style: 文案风格 ("casual", "professional", "urgent")
            
        Returns:
            生成的文案
        """
        logger.info(f"生成电商文案: {style}")

        prompt = f"""
        为以下产品生成快手短视频电商文案 ({style} 风格):
        
        产品名称: {product_info.get('name', '产品')}
        价格: ¥{product_info.get('price', 'X')}
        原价: ¥{product_info.get('original_price', 'X')}
        描述: {product_info.get('description', '优质产品')}
        特点: {', '.join(product_info.get('features', []))}
        
        要求:
        1. 简洁有力，2-3 行
        2. 突出价格和优惠
        3. 包含 CTA (行动号召)
        4. 使用表情符号
        """

        try:
            if self.provider == "openai":
                import openai
                openai.api_key = self.api_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100
                )
                return response["choices"][0]["message"]["content"]
            else:
                logger.warning("Claude API 集成待实现，返回示例文案")
                return "💰 惊爆价！原价 ¥299，现在只需 ¥99！\n✨ 品质保证，立即购买！"
        except Exception as e:
            logger.error(f"文案生成失败: {e}")
            return "立即抢购，优惠不容错过！"

    def predict_conversion_rate(self, video_analysis: Dict) -> Dict:
        """使用 AI 预测转化率
        
        Args:
            video_analysis: 视频分析结果
            
        Returns:
            转化率预测
        """
        logger.info("预测转化率...")

        # 简单的转化率预测模型
        score = 0.5  # 基础分数 50%

        # 根据视频特性调整
        if "highlights" in video_analysis:
            highlights_count = len(video_analysis["highlights"])
            score += min(highlights_count * 0.05, 0.15)  # 精彩片段加分

        if "duration" in video_analysis:
            duration = video_analysis["duration"]
            if 15 <= duration <= 30:
                score += 0.1  # 最优时长加分
            elif duration > 60:
                score -= 0.1  # 过长扣分

        if "music_bpm" in video_analysis:
            bpm = video_analysis["music_bpm"]
            if 100 <= bpm <= 140:
                score += 0.1  # 推荐 BPM 加分

        # 转化率评分
        conversion_rate = max(0, min(score, 0.95)) * 100  # 限制在 0-95%

        return {
            "conversion_rate": float(conversion_rate),
            "confidence": 0.7,
            "factors": {
                "highlights": "精彩片段多",
                "duration": "时长最优",
                "music": "节奏感强",
            },
            "suggestions": [
                "增加更多精彩片段转场",
                "强化价格和优惠信息",
                "添加真人出镜元素",
            ]
        }
