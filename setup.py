from setuptools import setup, find_packages

setup(
    name="async-news-scraper",
    version="2.0.0",
    description="An asynchronous news article collection system that scrapes Google News for specified topics",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Satyam-Rastogi/async_news_scraper",
    author="Satyam Rastogi",
    license="MIT",
    packages=find_packages(exclude=["tests*", "data*", "venv*"]),
    install_requires=[
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.1",
        "beautifulsoup4>=4.12.2",
        "requests>=2.32.3",
        "schedule>=1.2.0",
        "newspaper3k>=0.2.8",
        "Pillow>=10.0.0",
        "selectolax>=0.3.27",
        "httpx>=0.28.1",
        "PySocks>=1.7.1"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Text Processing :: Markup :: HTML",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "news-collector=src.core.main:main",
        ],
    },
    keywords="news scraper, google news, web scraping, async scraping, article extraction",
)