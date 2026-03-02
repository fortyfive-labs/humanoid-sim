FROM osrf/ros:humble-desktop-full

RUN apt-get update && apt-get install -y \
    gazebo \
    ros-humble-gazebo-ros \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-plugins \
    ros-humble-gazebo-msgs \
    ros-humble-xacro \
    ros-humble-rviz2 \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-tf2-tools \
    ros-humble-rosbag2-storage-mcap \
    liburdfdom-tools \
    git \
    wget \
    curl \
    libgl1-mesa-dri \
    libgl1-mesa-glx \
    mesa-utils \
    xvfb \
    x11-utils \
 && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /workspace
ENV COLCON_WS=/workspace

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
