from setuptools import setup, find_packages

setup(
    name="gps-dijkstra-dam",
    version="1.0.0",
    packages=find_packages(),
    description="Sistema GPS con algoritmo Dijkstra - Proyecto DAM",
    author="DAM Student",
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        'console_scripts': [
            'gps-dijkstra=main:main',
        ],
    },
)
