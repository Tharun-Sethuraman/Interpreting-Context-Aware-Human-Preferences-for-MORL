from setuptools import setup

setup(
    name="llm_context_predictor",
    py_modules=["llm_context_predictor"],
    version='0.0.1',
    description="This package uses llm to predict context of the environment and retrieve useful information",
    author="Tharun Sethuraman",
    # install_requires=['llama-index', 'typing', 'pyyaml',],
    python_requires=">=3.8",
)