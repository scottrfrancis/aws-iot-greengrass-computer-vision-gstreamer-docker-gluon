# RTSP grabber with GStreamer with Docker as a Greengrass component for CV Inference to Count People with Gluon CV

This project consists of three parts:

1. A Docker container to take an RTSP stream and extract the latest frame to a JPEG file
2. Building and deploying that container as a Greengrass v2 Component
3. A Gluon CV component to count people in that frame -- emitting the count, the bounding boxes, and frame rate stats over MQTT

This project targets Linux hosts and was developed using Linux and Mac desktop environments. 

## Part 1 - RTSP Stream to Still in a Docker Container

Using Computer Vision models often means acquiring images from RTSP sources. GStreamer provides a flexible and effective means to acquire those sources and render the current frame. As [GStreamer](https://gstreamer.freedesktop.org/) can require a number of libraries and be a bit tricky to work with, using Docker helps to manage these dependencies.

_Prerequisites_:

* [Install Docker](https://docs.docker.com/engine/install/)

### Step 1. Build the Docker image

The `RUN` command of the `Dockerfile` will install all the packages needed. The current build is based on Ubuntu 20.04, but it is certainly possible to create a smaller, more targetted image. 

Note the export of the Time Zone -- the GStreamer install will pause (and fail) if this is not set. 

[ ] set `TZ` to your [time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

the `CMD` provides the exec style params to the `ENTRYPOINT` -- these can be overridden by the docker invocation. Note the `location` parameter giving the RTSP source and the second `location` parameter giving the Docker-side path for the frame results.

[ ] customize the `location` for the `rtspsrc` for your source.

_Make sure you have the right source (IP, port, user, password) by using [VLC](https://www.videolan.org/vlc/) *and* with `telnet`, `nc`, or other from the Docker host to ensure the stream can be accessed._

[ ] (Optional) modify the `location` parameter for the `multifilesink` plugin to set the location of the file that the pipeline will write.

Now, build the image:

```bash
docker build --rm -t <name> .
```

The `--rm` switch will remove any previous builds (which you may accumulate if you change the `CMD` parameters or other settings). However, orphaned images can still accumulate. 

**List Images**
List images with

```bash
docker images
```

**Prune unused images**
```bash
docker system prune
```

### Step 2. Test the Docker Image

Start the docker container with

```bash
docker run -v /tmp:/data --user "$(id -u):$(id -g)" <name>
```

This will start the container, mapping the host's `/tmp` dir to the container's `/data` dir. New files will be created with the current user/group. 

**Normal output**
```
Progress: (open) Retrieving server options
Progress: (open) Retrieving media info
Progress: (request) SETUP stream 0
Progress: (request) SETUP stream 1
Progress: (open) Opened Stream
Setting pipeline to PLAYING ...
New clock: GstSystemClock
Progress: (request) Sending PLAY request
Progress: (request) Sending PLAY request
Progress: (request) Sent PLAY request
Redistribute latency...
```

Check the output with
```bash
# modify as needed if you changed the output location
ls -l /tmp/frame.jpg
```
and observe the user, group, timestamp, etc. 

Open the file in an image viewer and verify correctness.
_Tip_: on Ubuntu hosts, the command `eog /tmp/frame.jpg` will open a window with the image--it should refresh as the pipeline writes new frames.

_Troubleshooting_
Try executing the GStreamer pipeline interactively.

```bash
# launch the container in interactive mode
docker run -v  /tmp:/data --user "$(id -u):$(id -g)" -it --entrypoint /bin/bash gst
```
_(Errors about not having a name are normal.)_

Execute pipelines manually
```bash
# same command as in the Dockerfile
gst-launch-1.0 rtspsrc location="rtsp://<ip>:<port>/h264?username=<user>&password=<pass>" ! queue ! rtph264depay ! avdec_h264 ! jpegenc ! multifilesink location="/data/frame.jpg"

# capture the stream to a file until Ctrl-C cancels 
gst-launch-1.0 -e rtspsrc location="rtsp://192.168.5.193:554/h264?username=admin&password=123456" ! queue ! rtph264depay ! h264parse ! mp4mux ! filesink location=/data/file.mp4
```

Seeing errors about plugins missing or misconfigured?
```bash
# no rtspsrc? 
gst-inspect-1.0 rtspsrc
```

Compose additional pipelines, consulting the [GStreamer Plugin Reference](https://gstreamer.freedesktop.org/documentation/plugins_doc.html?gi-language=c)

### (Optional) Step 3. Use a RAM disk for the images

As the GStreamer pipeline will (re)write the frame file 30x/second, using a RAM Disk for these will save power and disk cycles as well as improve overall performance. When inference is added, we can extend the use of this RAM Disk.

* create entry in `/etc/fstab` 

```
tmpfs /tmp/gst tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=32M 0 0
```

creates 32M RAM disk in `/tmp/gst`...  the mapped volume for docker

Mount the RAM Disk with

```bash
sudo mount -a
```

You may need to `chown` the user/group of the created tmp dir **OR** execute subsequent inference with `sudo` **OR** modify the `fstab` entry to set the user/group.

