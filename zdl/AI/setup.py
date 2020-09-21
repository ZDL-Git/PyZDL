# coding:utf8
from setuptools import setup, find_namespace_packages


def get_version(rel_path):
    with open(rel_path, 'r') as f:
        for line in f.readlines():
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")


PACKAGES = find_namespace_packages(where='../../', include=['zdl.AI.*'])
PACKAGE_DATA = {}
REQUIRED_PACKAGES = [
    'numpy',
    'opencv-python',
    'PyZDL-utils @ git+https://github.com/ZDL-Git/PyZDL#subdirectory=zdl/utils',
]
VERSION = get_version('__init__.py')

print(':::version:::', VERSION)
print(':::packages:::', PACKAGES)

setup(
    name='PyZDL-AI',  # 安装后显示的包名，非导入名称
    version=VERSION,
    packages=PACKAGES,  # 导入名称
    package_dir={
        "zdl.AI": "../../zdl/AI",
    },
    package_data=PACKAGE_DATA,
    install_requires=REQUIRED_PACKAGES,
    python_requires=">=3.3",
    zip_safe=False,

    author_email="zdl_daily@163.com",
    description="This is an personal tool package. pip install git+https://github.com/ZDL-Git/PyZDL#subdirectory=zdl/AI",
    url="https://github.com/ZDL-Git/PyZDL/tree/master/zdl/AI",
)
