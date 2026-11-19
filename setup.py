"""安装配置：支持 pip install . 之后用 campus-ppt 命令。"""

from setuptools import setup, find_packages

from campus_ppt import __version__

setup(
    name="campus-ppt-studio",
    version=__version__,
    description="面向校园师生的原生可编辑 PPTX 生成器",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["python-pptx>=0.6.23"],
    entry_points={
        "console_scripts": [
            "campus-ppt=campus_ppt.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
