import os
import cv2
from threading import Lock
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseServerError
from django.shortcuts import render
import logging

# Force software decoding by setting the OPENCV_FFMPEG_CAPTURE_OPTIONS environment variable
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "video_codec;h264"

# Configure logging for detailed output
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global dictionary to store camera instances
cameras = {}

class VideoCamera:
    def __init__(self, source):
        self.source = source
        self.is_running = True
        self.lock = Lock()
        self.video = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
        if not self.video.isOpened():
            raise Exception(f"Failed to open video source: {source}")
        logger.debug(f"Camera initialized with source: {source}")

    def __del__(self):
        self.stop()

    def stop(self):
        with self.lock:
            if self.video:
                self.video.release()
                self.video = None
            self.is_running = False
            logger.debug("Camera stopped and video source released successfully.")

    def get_frame(self):
        with self.lock:
            if not self.is_running:
                return None
            ret, frame = self.video.read()
            if not ret:
                logger.error(f"Error capturing frame from {self.source}")
                self.stop()
                return None
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                logger.error(f"Error encoding frame from {self.source}")
                self.stop()
                return None
            return jpeg.tobytes()

def gen(camera):
    while camera.is_running:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            break

def video_feed(request, stream_id):
    stream_map = {
        "1": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/101",
        "2": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/201",
        "3": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/301",
        "4": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/401",
        "5": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/501",
        "6": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/601",
        "7": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/701",
        "8": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/801",
        "9": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/901",
        "10": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/1001",
        "11": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/1101",
        "12": "rtsp://admin:vct280620@10.11.12.122:1024/Streaming/Channels/1201",
        # Add more stream links as needed
    }
    source = stream_map.get(str(stream_id))
    if not source:
        logger.error(f"Invalid stream ID: {stream_id}")
        return HttpResponseServerError("Invalid stream ID")

    if str(stream_id) not in cameras:
        try:
            cameras[str(stream_id)] = VideoCamera(source)
            logger.debug(f"Camera created for stream ID: {stream_id}")
        except Exception as e:
            logger.error(f"Failed to initialize camera for stream {stream_id}: {e}")
            return HttpResponseServerError(str(e))

    camera = cameras[str(stream_id)]
    return StreamingHttpResponse(gen(camera), content_type="multipart/x-mixed-replace; boundary=frame")

def control_stream(request, stream_id, action):
    logger.debug(f"Received control request: stream_id={stream_id}, action={action}")
    camera = cameras.get(str(stream_id))
    if not camera:
        logger.error(f"Camera not found for stream ID: {stream_id}")
        return JsonResponse({'status': 'error', 'message': 'Invalid stream ID'}, status=400)

    if action not in ['pause', 'play']:
        logger.error(f"Invalid action attempted: {action}")
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    if action == 'pause':
        camera.is_running = False
        logger.info(f"Camera {stream_id} paused")
    elif action == 'play':
        camera.is_running = True
        logger.info(f"Camera {stream_id} resumed")

    return JsonResponse({'status': 'success', 'action': action, 'stream_id': stream_id})

def live_stream_page(request, page_num):
    # Define the streams per page
    streams_per_page = 6
    # Calculate the start and end indices for streams on the current page
    start_idx = (page_num - 1) * streams_per_page
    end_idx = page_num * streams_per_page
    # Get the list of stream IDs for the current page
    stream_ids = list(range(1, 13))[start_idx:end_idx]  # Assuming 12 streams in total
    context = {
        'stream_ids': stream_ids,
        'page_num': page_num,
    }
    # Choose the template based on the page number
    template_name = 'live_stream_page1.html' if page_num == 1 else 'live_stream_page2.html'
    return render(request, f'live1/{template_name}', context)
