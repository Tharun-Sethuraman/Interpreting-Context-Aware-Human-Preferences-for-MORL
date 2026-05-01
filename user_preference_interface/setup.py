from setuptools import setup

setup(
    name="user_preference_interface",
    py_modules=["user_preference_interface"],
    version='0.0.1',
    description="This package combines the functional blocks context predictor, rule updater and preference translator",
    author="Tharun Sethuraman",
    # install_requires=['llama-index', 'typing', 'pyyaml',],
    python_requires=">=3.8",
)