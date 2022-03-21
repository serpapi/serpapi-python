from setuptools import setup, find_packages
from codecs import open
from os import path
from pathlib import Path
long_description = (Path(__file__).parent / "README.md").read_text()

setup(name='serpapi',
      version='1.0.0',
      description='Scrape and search localized results from Google, Bing, Baidu, Yahoo, Yandex, Ebay, Homedepot, youtube at scale using SerpApi.com',
      url='https://github.com/serpapi/serpapi-python',
      author='vikoky',
      author_email='victor@serpapi.com',
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Natural Language :: English',
        'Topic :: Utilities',
        ],
    python_requires='>=3.5',
    zip_safe=False,
    include_package_data=True,
    license="MIT",
    install_requires = ["urllib3"],
    packages=find_packages(),
    keywords='scrape,serp,api,json,search,localized,rank,google,bing,baidu,yandex,yahoo,ebay,scale,datamining,training,machine,ml,youtube,naver,walmart,apple,store,app,serpapi',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
