FROM nvcr.io/nvidia/doca/doca:3.1.0-devel-host

ENV TZ=US DEBIAN_FRONTEND=noninteractive

# Update and install build dependencies
# (Optimize docker image size with `rm -rf /var/lib/apt/lists/*`)
# (Remove outdated meson)
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y remove meson && \
    apt-get -y install \
    ninja-build \
    python3-numpy \
    python3-dev \
    python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install meson && \
    python3 -m pip install pybind11

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Build the application
RUN meson setup builddir-release -Dbuildtype=release && \
    meson compile -C builddir-release

ENV PYTHONPATH=/app/builddir-release

# Set default command to run as server
CMD ["./builddir-release/example_cpp", "--server", "192.168.200.13:5000"]