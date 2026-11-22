import os
from glob import glob

from setuptools import setup

package_name = "darkpaw_test"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Konstantin Blednov",
    maintainer_email="konstantin.blednov@outlook.com",
    description="/cmd_vel contour check: logs incoming commands",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "listener = darkpaw_test.listener:main",
        ],
    },
)
