from setuptools import setup

setup(name='flir_ir',
      version='1.0.0',
      packages=['flir_ir'],
      include_package_data=True,
      install_requires=[
          'utm', 
          'python-dateutil',
          'influxdb',
      ],
      url='https://github.com/terraref/flir_ir',
      )