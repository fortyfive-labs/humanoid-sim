from setuptools import find_packages, setup

package_name = 'g1_apps'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Developer',
    maintainer_email='user@example.com',
    description='Robot programs for the Unitree G1',
    license='BSD',
    entry_points={
        'console_scripts': [
            # Example nodes — add your own programs here following the same pattern:
            # 'my_node = g1_apps.my_node:main',
            'sensor_monitor = g1_apps.sensor_monitor:main',
            'joint_commander = g1_apps.joint_commander:main',
        ],
    },
)
