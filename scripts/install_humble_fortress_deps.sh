#!/usr/bin/env bash
set -euo pipefail

if [[ "$(lsb_release -cs)" != "jammy" ]]; then
  echo "This installer targets Ubuntu 22.04 Jammy for ROS 2 Humble." >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y \
  curl \
  gnupg \
  lsb-release \
  locales \
  python3-pip \
  software-properties-common

sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

sudo add-apt-repository -y universe

sudo install -m 0755 -d /etc/apt/keyrings

if [[ ! -f /etc/apt/keyrings/ros-archive-keyring.gpg ]]; then
  curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    | sudo gpg --dearmor -o /etc/apt/keyrings/ros-archive-keyring.gpg
fi

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list >/dev/null

if [[ ! -f /etc/apt/keyrings/pkgs-osrf-archive-keyring.gpg ]]; then
  curl -sSL https://packages.osrfoundation.org/gazebo.gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/pkgs-osrf-archive-keyring.gpg
fi

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable jammy main" \
  | sudo tee /etc/apt/sources.list.d/gazebo-stable.list >/dev/null

sudo apt-get update

sudo apt-get install -y \
  gz-fortress \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-vcstool \
  ros-dev-tools \
  ros-humble-cartographer-ros \
  ros-humble-desktop \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-navigation2 \
  ros-humble-robot-state-publisher \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-rqt-robot-steering \
  ros-humble-slam-toolbox \
  ros-humble-tf-transformations \
  ros-humble-turtlesim \
  ros-humble-xacro

if apt-cache show ros-humble-ros-gz >/dev/null 2>&1; then
  sudo apt-get install -y ros-humble-ros-gz
else
  sudo apt-get install -y \
    ros-humble-ros-ign \
    ros-humble-ros-ign-bridge \
    ros-humble-ros-ign-gazebo
fi

if ! rosdep --version >/dev/null 2>&1; then
  echo "rosdep was not installed correctly." >&2
  exit 1
fi

if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  sudo rosdep init
fi

rosdep update

if ! grep -q "source /opt/ros/humble/setup.bash" "$HOME/.bashrc"; then
  echo "source /opt/ros/humble/setup.bash" >> "$HOME/.bashrc"
fi

echo
echo "Installed ROS 2 Humble, Gazebo Fortress, rosdep, and workspace build tools."
echo "Open a new terminal or run: source /opt/ros/humble/setup.bash"
