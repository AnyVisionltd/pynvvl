#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import re
import shutil
import subprocess
import sys
import sysconfig

from Cython.Distutils import build_ext
from pkg_resources import get_distribution
from setuptools import Extension
from setuptools import setup


CUDA_VERSION = subprocess.check_output(
    'nvcc -V | grep -oP "release\s([0-9\.]+)" | grep -oP "([0-9\.]+)"',
    shell=True).decode('utf-8').strip()


def create_extensions():
    sourcefiles = [
        'pynvvl/_nvvl.pyx',
    ]

    # List up include paths
    include_dirs = [
        os.path.join(os.getcwd(), 'docker/include'),
        '/usr/local/cuda/include',
        sysconfig.get_config_var('INCLUDEPY'),
    ]
    if 'CPATH' in os.environ:
        include_dirs.insert(1, os.environ['CPATH'])

    # List up library paths
    library_dirs = [
        os.path.join(os.getcwd(), 'docker/lib/cuda-{}'.format(CUDA_VERSION)),
    ]
    if 'LD_LIBRARY_PATH' in os.environ:
        library_dirs.append(os.environ['LD_LIBRARY_PATH'])
    if 'LIBRARY_PATH' in os.environ:
        library_dirs.append(os.environ['LIBRARY_PATH'])

    # List up libraries
    libraries = [
        'nvvl',
    ]

    # RPATH which will be set to pynvvl.so
    rpath = [
        '$ORIGIN/_lib',
    ]

    extensions = [
        Extension(
            'pynvvl._nvvl',
            sourcefiles,
            include_dirs=include_dirs,
            library_dirs=library_dirs,
            libraries=libraries,
            language='c++',
            extra_compile_args=['-std=c++11'],
            extra_link_args=['-std=c++11'],
            runtime_library_dirs=rpath,
        )
    ]
    return extensions


def find_lib_from_pathlist(libname, pathlists, **kwargs):
    """Find library file from a list of paths"""

    include_ver_variants = kwargs.pop('include_ver_variants', True)
    include_library_path = kwargs.pop('include_library_path', True)

    # pathlists is a list of strings (e.g. LIBRARY_PATH) or lists of paths
    # so path_lists is a flattened list of directory paths
    path_list = []
    for lst in pathlists:
        if type(lst) is str:
            lst = re.split(r':', lst)
        path_list += lst

    if include_library_path:
        path_list += re.split(r':', os.environ.get('LIBRARY_PATH') or "")

    for path in path_list:
        try:
            files = os.listdir(path)
        except IOError:
            continue

        if libname in files:
            return os.path.join(path, libname)

        if include_ver_variants:
            regexp = re.escape(libname) + r'\.\d+$'
            libs = [f for f in files if re.match(regexp, f)]
            if len(libs) > 0:
                return os.path.join(path, libs[0])

    raise RuntimeError("Cannot find a library '{}' "
                       "in the specified paths".format(libname))


def prepare_package_data():
    lib_names = [
        'libnvvl.so',
        'libavformat.so',
        'libavfilter.so',
        'libavcodec.so',
        'libavutil.so',
    ]
    docker_lib_dir = 'docker/lib/cuda-{}'.format(CUDA_VERSION)
    wheel_libs = [find_lib_from_pathlist(l, [docker_lib_dir]) for l in lib_names]

    lib_dir = 'pynvvl/_lib'
    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)
    libs = []
    for lib in wheel_libs:
        libname = os.path.basename(lib)
        libpath = os.path.join(lib_dir, libname)
        shutil.copy2(lib, libpath)
        libs.append(os.path.join('_lib', libname))

    package_data = {
        'pynvvl': libs
    }

    return package_data


parser = argparse.ArgumentParser()
parser.add_argument('--package-name', type=str, default='pynvvl')
args, sys.argv = parser.parse_known_args(sys.argv)

package_data = prepare_package_data()
extensions = create_extensions()

cupy_package_name = None
try:
    cupy_package_name = get_distribution(
        'cupy-cuda{}'.format(CUDA_VERSION.replace('.', '')))
    cupy_package_name = cupy_package_name.project_name
except Exception:
    cupy_package_name = 'cupy'

print('=' * 30)
print('CuPy Package Name:', cupy_package_name)
print('=' * 30)

description = \
    'PyNVVL: A Python wrapper for NVIDIA Video Loader (NVVL) with CuPy'

setup(
    name=args.package_name,
    url='https://github.com/mitmul/pynvvl',
    version='0.0.3a2',
    author='Shunta Saito',
    author_email='shunta.saito@gmail.com',
    description=description,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT License',
    packages=['pynvvl'],
    package_data=package_data,
    install_requires=[
        '{}>=4.5.0'.format(cupy_package_name),
    ],
    setup_requires=[
        'cython>=0.28.0',
    ],
    ext_modules=extensions,
    cmdclass={'build_ext': build_ext},
)
