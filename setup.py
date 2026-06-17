from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="auto-video-editor",
    version="0.1.0",
    author="dwu40657",
    description="AI-powered automatic video editing for Kuaishou short-form commerce",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwu40657/auto-video-editor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "moviepy>=1.0.3",
        "librosa>=0.10.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "openai>=1.0.0",
        "pydub>=0.25.0",
        "Pillow>=10.0.0",
        "PyYAML>=6.0",
        "requests>=2.31.0",
    ],
)
