# Auto Video Editor - 快手短视频自动剪辑工具

专为快手电商带货场景优化的 AI 自动视频剪辑工具。一键生成高转化率的短视频内容。

## 功能特性

- 🎬 **智能视频分析** - 自动检测产品展示、精彩片段、转场点
- 📝 **动态字幕生成** - 语音转文字，支持带货文案优化
- 🎵 **音乐节奏同步** - 自动检测音乐节奏，匹配视频剪辑
- ✂️ **快手优化剪辑** - 自动裁剪、转场、抖动效果
- 🎯 **带货转化优化** - 突出产品、价格、福利信息
- 📊 **效果预测** - AI 预测转化率和推荐优化

## 快手平台规格

| 规格项 | 参数 |
|--------|------|
| 视频比例 | 9:16 (竖屏) |
| 推荐分辨率 | 1080x1920 |
| 视频时长 | 15s-60s（带货最优15-30s） |
| 帧率 | 30fps |
| 码率 | 5-8Mbps |
| 音频采样率 | 48kHz |

## 快速开始

### 1. 安装

```bash
git clone https://github.com/dwu40657/auto-video-editor.git
cd auto-video-editor
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
export OPENAI_API_KEY=your_key
export VIDEO_OUTPUT_DIR=./outputs
export KUAISHOU_ENABLED=true
```

### 3. 基本使用

```python
from src.main import VideoEditor

# 创建编辑器实例
editor = VideoEditor(
    video_path="product_demo.mp4",
    platform="kuaishou",
    ai_provider="openai"
)

# 处理视频
result = editor.process()
print(f"输出: {result['output_path']}")
print(f"预测转化率: {result['conversion_rate']}%")
```

## 工作流程

```
原始视频 (任意格式)
    ↓
[1. 视频分析]
├─ 检测产品展示区间
├─ 识别精彩片段
├─ 分析音乐节奏
└─ 检测转场点
    ↓
[2. 快手优化]
├─ 裁剪为 9:16
├─ 优化视频长度 (15-30s)
├─ 检测和突出产品
└─ 添加快手特效
    ↓
[3. 字幕生成]
├─ 语音转文字
├─ AI 生成带货文案
├─ 添加价格/福利信息
└─ 优化字幕位置
    ↓
[4. 音乐同步]
├─ 选择节奏感强的背景音乐
├─ 匹配音乐节奏
└─ 调整音量
    ↓
[5. 特效处理]
├─ 添加转场
├─ 抖动/缩放效果
├─ 闪光/强调效果
└─ 字幕动画
    ↓
[6. 转化率预测]
├─ AI 评分内容质量
├─ 预测用户吸引度
└─ 提供优化建议
    ↓
输出高转化率视频 (1080x1920, MP4)
```

## 依赖

- Python 3.8+
- FFmpeg
- MoviePy
- OpenAI API / Claude API
- librosa (音乐分析)
- SpeechRecognition (语音识别)

## 许可证

MIT

## 联系方式

有问题或建议？欢迎提交 Issue 或 PR！
