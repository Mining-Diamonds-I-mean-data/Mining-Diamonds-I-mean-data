# Python Import Index

This Undergraduate research project was done by Kolby Moroz Liebl and Marafi Mergani with research department UAlberta Software Maintenance and Reuse (SMR) at the University of Alberta. Our supervisors were Mohayeminul Islam and Sarah Nadi

Instructions for using the tools we created locally will be provided below, but instructions to deploy our "Flask API Interface" will not be provided

# Readme Index
- [Requirements](#requirements)
- [Setup Instructions Ubuntu](#setup-instructions-ubuntu)
- [Initialize/Update dataset](#initializeupdate-dataset)
- [Run Flask API Interface](#run-flask-api-interface)
- [Examples of interacting with the Flask API Interface](#examples-of-interacting-with-the-flask-api-interface)
  - [Examples of /library/ api](#examples-of-library-api)
  - [Examples of /importname/ api](#examples-of-importname-api)
  - [Examples of /dump api](#examples-of-dump-api)

# Requirements

- python 3.11+
- postgres
- git

# Setup Instructions Ubuntu
We assume you already have Postgres installed.

Our interface to the database is using a rest api built using Flask

Clone the project
```shell
git clone https://github.com/ualberta-smr/Python-Import-Index.git
```

Enter the directory
```shell
cd Python-Import-Index
```

Initialize Python Virtual Environment
```shell
python3 -m venv venv
. venv/bin/activate
```

Install project library requirements
```shell
pip install -r requirements.txt
```

# Initialize/Update dataset
Run this script when you want to Initialize/Update the dataset. If you want to speed this process up you can configure the amount of python processes collecting the data in the file
```shell
python run-this-to-initialize-and-update-dataset.py
```

# Run Flask API Interface
Run this script to launch the python Flask interface for the project
```shell
python app.py
```

# Examples of interacting with the Flask API Interface
Run this script to launch the python Flask interface for the project
```shell
python app.py
```
You should get
```
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```
Take the url provided in this case ``http://127.0.0.1:5000``

### Examples of /library/ api
This api takes a library's name and provides the respective library import names
- libraries are comma separated
- optional version argument can be added “:x.y.z” e.x. “discord.py:0.11.0”

So you can enter ``http://127.0.0.1:5000/library/discord.py:0.11.0,setuptools`` into your browser and get

```json
{
    "error": [],
    "result": [
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.11.0"
        },
        {
            "import_name": "pkg_resources",
            "library_name": "setuptools",
            "version": "67.8.0"
        },
        {
            "import_name": "setuptools",
            "library_name": "setuptools",
            "version": "67.8.0"
        },
        {
            "import_name": "pkg_resources",
            "library_name": "setuptools",
            "version": "68.0.0"
        },
        {
            "import_name": "setuptools",
            "library_name": "setuptools",
            "version": "68.0.0"
        },
        {
            "import_name": "pkg_resources",
            "library_name": "setuptools",
            "version": "68.1.0"
        },
        {
            "import_name": "setuptools",
            "library_name": "setuptools",
            "version": "68.1.0"
        },
        {
            "import_name": "pkg_resources",
            "library_name": "setuptools",
            "version": "68.2.0"
        },
        {
            "import_name": "setuptools",
            "library_name": "setuptools",
            "version": "68.2.0"
        },
        {
            "import_name": "pkg_resources",
            "library_name": "setuptools",
            "version": "69.0.0"
        },
        {
            "import_name": "setuptools",
            "library_name": "setuptools",
            "version": "69.0.0"
        }
    ]
}
```

### Examples of /importname/ api
This api takes a library import names and provides the respective library names
- libraries are comma separated
- this api endpoint doesn't provide a version argument

So you can enter ``http://127.0.0.1:5000/importname/discord,pkg_resources`` into your browser and get

```json
{
    "error": [],
    "result": [
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.10.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.11.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.12.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.13.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.14.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.15.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.16.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.4.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.5.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.6.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.7.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.8.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "0.9.0"
        },
        {
            "import_name": "discord",
            "library_name": "discord.py",
            "version": "2.3.0"
        },
        {
            "import_name": "pkg_resources",
            "library_name": "setuptools",
            "version": "67.8.0"
        },
        {
            "import_name": "pkg_resources",
            "library_name": "setuptools",
            "version": "68.0.0"
        },
        {
            "import_name": "pkg_resources",
            "library_name": "setuptools",
            "version": "68.1.0"
        },
        {
            "import_name": "pkg_resources",
            "library_name": "setuptools",
            "version": "68.2.0"
        },
        {
            "import_name": "pkg_resources",
            "library_name": "setuptools",
            "version": "69.0.0"
        }
    ]
}
```

### Examples of /dump api
If you want a csv dump of our database run ``http://127.0.0.1:5000/dump`` in your browser

