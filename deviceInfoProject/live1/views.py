#live stream
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.gzip import gzip_page
from django.shortcuts import render
import cv2

class VideoCamera(object):
    def __init__(self, sources):
        self.videos = []
        for source in sources:
            video = cv2.VideoCapture(source)
            if not video.isOpened():
                raise ValueError(f"Unable to open video source: {source}")
            self.videos.append(video)

    def __del__(self):
        for video in self.videos:
            if video.isOpened():
                video.release()

    def get_frames(self):
        frames = []
        for video in self.videos:
            ret, frame = video.read()
            if not ret:
                frames.append(None)
                continue
            ret, jpeg = cv2.imencode('.jpg', frame)
            frames.append(jpeg.tobytes())
        return frames

def gen(camera):
    while True:
        frames = camera.get_frames()
        for frame in frames:
            if frame is None:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def live_stream(request):
    return render(request, 'live1/live_stream.html')

@gzip_page
def video_feed(request, stream_id):
    try:
        sources = [
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/101",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/201",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/301",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/401",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/501",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/601",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/701",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/801",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/901",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/1001",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/1101",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/1201",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/1301",
             "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/1401",
        ]
        return StreamingHttpResponse(gen(VideoCamera(sources[int(stream_id)-1:int(stream_id)])), content_type="multipart/x-mixed-replace;boundary=frame")
    except ValueError as e:
        return render(request, 'info/error.html', {'error_message': str(e)})
