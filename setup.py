#! /usr/bin/env python
from distutils.core import setup, Extension

m = Extension('_kmsg',
        sources = ['kmsg.c'] 
        )


setup(name = 'kmsg',
        version = '0.01',
        description = 'python library for /dev/kmsg (printk)',
        py_modules = ["kmsg"],
        ext_modules = [m])
