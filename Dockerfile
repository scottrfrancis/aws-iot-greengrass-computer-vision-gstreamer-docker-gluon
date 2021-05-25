FROM ubuntu:20.04
ENV TZ=<your timezone, e.g. America/Los_Angeles>
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && apt-get install -y \
    libgstreamer1.0-0  \
	gstreamer1.0-plugins-base \
	gstreamer1.0-plugins-good \
	gstreamer1.0-plugins-bad \
	gstreamer1.0-plugins-ugly \
	gstreamer1.0-libav \
	gstreamer1.0-doc \
	gstreamer1.0-tools \
	gstreamer1.0-x \
	gstreamer1.0-alsa \
	gstreamer1.0-gl \
	gstreamer1.0-gtk3 \
	gstreamer1.0-qt5 \
	gstreamer1.0-pulseaudio \
	&& apt-get clean && apt-get autoremove && rm -rf /var/lib/apt/lists/*
	
ENTRYPOINT ["gst-launch-1.0"] 
CMD ["rtspsrc", "location=\"rtsp://<ip>:<port>/h264?username=<user>&password=<pass>\"", "!", "queue", "!", "rtph264depay", "!", "avdec_h264", "!", "jpegenc", "!", "multifilesink", "location=\"/data/frame.jpg\""]
