from setuptools import setup, find_packages

setup(
    name='BoxUtils',
    version='0.1.9',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'box_sdk_gen[jwt]',
    ],
    entry_points={

    },
    author='Kelvin O. Lim',
    author_email='lim.kelvino@gmail.com',
    description='A utility package for performing Box file and folder operations with a service account',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/kelvinlim/BoxUtils',  # Update with your repository URL
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
