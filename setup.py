from setuptools import setup, find_packages

setup(
    name="pastepal",
    version="1.0.0",
    description="A powerful Windows clipboard manager with advanced features",
    author="PastePal Team",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.1",
        "pywin32>=306",
        "keyboard>=0.13.5",
        "Pillow>=10.1.0",
        "pyinstaller>=6.3.0",
    ],
    entry_points={
        "console_scripts": [
            "pastepal=pastepal.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
)
