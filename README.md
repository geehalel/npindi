# npindi

Native Python Indi library is an implementation of the INDI library written in pure Python. It does not rely on
an underlying C/C++ INDI library as [pyindi-client](https://pypi.python.org/pypi/pyindi-client) does.
At the moment it only implements the client side of the INDI library. I may also implement the driver side later.

This project contains (all this is **work in progress**):
* the native Python INDI framework in `/indi/` directory:
  *  `indi/indibase` contains the `basedevice` and `baseclient` classes. The latter generates the `new*` and `set*` callbacks, that your own client should implement. The `basemediator` class is such a default implementation which does nothing but logging. As I am still not sure how to use this framework from Python (the `baseclient` runs in its own thread, thus the callbacks are run in that thread), I also implement a `baseclientqt` class which uses the Qt signalling mechanism, which is safer.
  * `indi/client/` contains client classes: `indiclient` is a try to propose an API for using the framework in Python. It is based on event queuing, but it is still work in progress.
  * `indi/client/qt` contains a Python rewrite of the INDI client API used in KStars. It implements the Driver Manager and the Control Panel that you can easily add to your Qt application. Concerning the driver API, only the telescope and CCD classes have been ported.
* some testing scripts/applications in `/tests/` directory, particularly the `testapi.py` Qt application which allows to browse methods and signals defined by the above Kstars API implementation.
* some demo applications in `apps` directory:
  * `mountHC` is a simple Hand-Controller for INDI telescope devices
  * `mount3D` is a PyQt3D application which displays an equatorial mount (EQ5) in a 3D view when it is connected to an INDI telescope device. The 3D view follows the telescope moves as reported by the INDI device. Beware that the application reads UTC time from the device, but as it is now left unchanged in devices after connection from KStars, connect the application just after connecting the telescope from KStars.

To install the framework, simply change directory to `indi/` and use the setup script to install the framework in your Python user library:
`python3 setup.py install --user`

The test and demo applications may be run from their respective directories after you have installed the framework. You may need to install PyQt3D for the `mount3D` demo. Just use `pip3 install pyqt3d --user`, it comes with PyQt5 and its own Qt5 libraries, which is really helpful. Here are some screenshots of these applications.

| Mount Hand Controller      |   API test application |
|----------------------------|------------------------|
| ![mounthc]                 | ![testapi]             |


Mount3D pointing Pleiades
 ![Mount3D][mount3d]

 The control Panel
 ![Control Panel][cp]

[mounthc]: docs/screenshots/mountHC.png "Mount Hand Controller"
[testapi]: docs/screenshots/testapi.png "The API test application"
[cp]: docs/screenshots/control-panel.png "Control panel"
[mount3d]: docs/screenshots/mount3D.png "Mount3D pointing Pleiades"
