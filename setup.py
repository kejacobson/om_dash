from setuptools import setup, find_packages

__package_name__ = "om_dash"
__package_version__ = "0.0.1"


setup(
    name=__package_name__,
    version=__package_version__,
    description=("Simple GUI demo for OpenMDAO"),
    scripts=['om_dash/monitor_opt.py',
             'om_dash/om_convert_recorder_hist.py',
             'om_dash/om_plot_recorder_hist.py'],
    author="Kevin Jacobson",
    author_email="kevin.e.jacobson@nasa.gov",
    zip_safe=False,
    packages=find_packages()
)
