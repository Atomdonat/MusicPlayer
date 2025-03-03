from setuptools import setup, find_packages


setup(
    name='MusicPlayer',
    version='1.15.7',
    url='https://github.com/Atomdonat/MusicPlayer.git',
    license='GPLv3',
    author='Atomdonat',
    author_email='busterbox2@gmail.com',
    description="A Python project for interacting with the Spotify Web API",
    long_description=open("README.md", "r", encoding="utf-8").read(),
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