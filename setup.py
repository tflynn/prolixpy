from setuptools import setup, find_packages

setup(
    name='prolix',
    version='0.1',
    description='Experiments in stenography (Python)',
    url='https://github.com/tflynn/prolixpy.git',
    author='Tracy Flynn',
    author_email='tracysflynn@gmail.com',
    license='MIT',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={
        'prolix': ['*.json','**/*.json']
    },
    install_requires=[
        'standard_logger>=0.4',
        'run_command>=1.0',
        'words>=0.1',
        'redis>=2.10.6',
        "pyxutils>=0.1",
        "json_config>=0.1"],
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False
)
