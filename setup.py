from setuptools import setup, find_packages

setup(
    name = 'simple-social-suture',
    version = '0.5',
    author = 'Nina Pavlich',
    author_email='nina@ninalp.com',
    url = 'https://github.com/ninapavlich/simple-social-suture',
    license = "MIT",
    description = 'Retrieve and combine content from various social networks into a unified format',
    keywords = ['libraries', 'web development', 'social network', 'python', 'twitter', 'instagram'],
    include_package_data = True,
    packages = ['simple_social_suture'],
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)