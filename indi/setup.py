# Copyright 2017 geehalel@gmail.com
#
# This file is part of npindi.
#
#    npindi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    npindi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with npindi.  If not, see <http://www.gnu.org/licenses/>.

# python3 setup.py build -b /tmp/indi install --user
from distutils.core import setup

setup(
    name="indi",
    version="0.1",
    packages=['indi', 'indi.client', 'indi.indibase', 'indi.client.qt'],
    package_data={'indi.client.qt': ['drivermanager.ui', 'indihostconf.ui']},
    author="geehalel",
    author_email="geehalel@gmail.com",
    url="https://github.com/geehalel/npindi",
    license='GNU General Public License v3 or later (GPLv3+)',
    description="""Third party Native Python API for INDI""",
    #long_description=readme.read(),
    #long_description=descr,
    keywords=["libindi client"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix, Windows",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Astronomy"
        ],

)
