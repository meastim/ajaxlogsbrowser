from setuptools import setup

setup(
    name = "ajaxlogsbrowser",
    version = "0.1",
    author = "Bruno Harbulot",
    description = ("A web application to view log files."),
    license = "MIT",
    keywords = "logs web",
    packages=['ajaxlogsbrowser'],
    package_data = {
        '': [
                'js/*.*',
                'templates/*.*',
                '3rdparty/*.*',
                '3rdparty/jquery-ui/*/*.*',
                '3rdparty/jquery-ui/*/*/*.*',
                '3rdparty/jquery-ui/*/*/*/*.*',
                '3rdparty/SlickGrid/*.*',
                '3rdparty/SlickGrid/lib/*.*',
                '3rdparty/SlickGrid/images/*.*',
                '3rdparty/SlickGrid/plugins/*.*',
                '3rdparty/SlickGrid/examples/*.*'
            ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)