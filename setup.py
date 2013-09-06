from setuptools import setup, find_packages


setup_args = dict(
    name='lipy',
    version='0.1',
    description='Python API wrapper for Linode - https://www.linode.com',
    maintainer='Nick Joyce',
    maintainer_email='nick@boxdesign.co.uk',
    packages=find_packages('.')
)


if __name__ == '__main__':
    setup(**setup_args)
