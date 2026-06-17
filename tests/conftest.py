"""测试配置和工具"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 测试数据目录
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# 测试输出目录
TEST_OUTPUT_DIR = Path(__file__).parent / "test_outputs"
TEST_OUTPUT_DIR.mkdir(exist_ok=True)


def create_test_video(duration: float = 5.0) -> str:
    """创建测试视频
    
    Args:
        duration: 视频时长（秒）
        
    Returns:
        测试视频路径
    """
    try:
        from moviepy.editor import ColorClip, concatenate_videoclips
        import numpy as np
        
        output_path = TEST_DATA_DIR / "test_video.mp4"
        
        if output_path.exists():
            return str(output_path)
        
        # 创建彩色视频（黑色背景）
        clips = []
        for i in range(int(duration)):
            # 创建不同颜色的帧以模拟场景变化
            color = (np.random.randint(0, 100), np.random.randint(0, 100), np.random.randint(0, 100))
            clip = ColorClip(size=(1080, 1920), color=color).set_duration(1)
            clips.append(clip)
        
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(str(output_path), verbose=False, logger=None, fps=30)
        
        print(f"✅ 测试视频创建成功: {output_path}")
        return str(output_path)
    except Exception as e:
        print(f"❌ 测试视频创建失败: {e}")
        return ""


def cleanup_test_outputs():
    """清理测试输出"""
    import shutil
    if TEST_OUTPUT_DIR.exists():
        shutil.rmtree(TEST_OUTPUT_DIR)
        TEST_OUTPUT_DIR.mkdir(exist_ok=True)
        print("✅ 测试输出已清理")
