from setuptools import setup, find_packages

setup(
    name="ara-financial-agent",
    version="1.0.0",
    description="ARA-1: Autonomous Financial Research Agent with Multi-Source Synthesis",
    author="Aswin Kumar (QuantumEdge Research / Zetheta)",
    author_email="aswin.kumar@quantumedge.ai",
    packages=find_packages(include=["agent*", "tools*", "memory*", "synthesis*", "evaluation*"]),
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.7.0",
        "requests>=2.31.0",
        "httpx>=0.27.0",
        "tenacity>=8.3.0",
        "rich>=13.7.1",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "ara-agent=agent.core:main",
            "ara-eval=evaluation.dashboard:main",
        ]
    }
)
