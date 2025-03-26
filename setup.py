from setuptools import setup, find_packages
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
readme_path = os.path.join(base_dir, "README.md")

setup(
    name='MusicPlayer',
    version='1.16.0',
    url='https://github.com/Atomdonat/MusicPlayer.git',
    license='GPLv3',
    author='Atomdonat',
    author_email='busterbox2@gmail.com',
    description="A Python project for interacting with the Spotify Web API",
    long_description=open(readme_path, "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests",
        "spotipy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
)