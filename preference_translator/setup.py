from setuptools import setup

setup(
    name="preference_translator",
    py_modules=["preference_translator"],
    version='0.0.1',
    description="This package uses llm translate the contextual information and explainable rule set into preference vector",
    author="Tharun Sethuraman",
    # install_requires=['llama-index', 'typing', 'pyyaml',],
    python_requires=">=3.8",
)