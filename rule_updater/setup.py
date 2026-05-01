from setuptools import setup

setup(
    name="rule_updater",
    py_modules=["rule_updater"],
    version='0.0.1',
    description="This package uses llm to compile the rules from human feedback into rule set",
    author="Tharun Sethuraman",
    # install_requires=['llama-index', 'typing', 'pyyaml',],
    python_requires=">=3.8",
)