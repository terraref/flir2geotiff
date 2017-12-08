from setuptools import setup

setup(name='flir2geotiff',
      version='1.0.0',
      packages=['flir2geotiff'],
      include_package_data=True,
      install_requires=[
          'utm', 
          'python-dateutil',
          'influxdb',
      ],
      url='https://github.com/terraref/flir2geotiff',
      )