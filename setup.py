from setuptools import find_packages, setup

setup(
    name='seiacodingchallenge',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'coverage==6.4.1',
        'Flask==2.1.2',
        'flask-expects-json==1.7.0',
        'Flask-RESTful==0.3.9',
        'gunicorn==20.1.0',
        'numpy==1.19.5',
        'pytest==7.0.1',
        'pytz==2022.1',
        'wheel==0.37.1'
    ],
)