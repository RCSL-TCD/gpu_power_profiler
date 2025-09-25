from setuptools import setup, find_packages

setup(
    name='gpu_profiler',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas',
        'joblib',
        'loguru',
        'scikit-learn',
         'numpy',
        'scikit-learn'        
    ],
    entry_points={
        'console_scripts': [
            'gpu_profiler=gpu_profiler.gpu_profiler:main',
        ],
    },
    author='Your Name',
    description='GPU power prediction tool using Nsight Compute',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
