from .forms import UserRegisterForm
import requests
import xmltodict
import logging
from django.shortcuts import render, redirect
from requests.auth import HTTPDigestAuth
import cv2
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)

@login_required
def charts(request):
    # Define the context variable
    context = {}
    return render(request, 'info/charts.html', context)

@login_required
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'info/register.html', {'form': form})

@login_required
def profile(request):
    # Your logic for the profile view
    return render(request, 'profile.html')


def dashboard(request):
    context = {
        'company_name': 'VC TECH',
        'description': 'We provide innovative tech solutions to modern problems.',
    }
    return render(request, 'info/dashboard.html', context)


#live stream
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.gzip import gzip_page

@login_required
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

@login_required
def live_stream(request):
    return render(request, 'info/live_stream.html')

@login_required
@gzip_page
def video_feed(request, stream_id):
    try:
        sources = [
            'rtsp://vctech:Vctech@1234@192.168.2.114:4345/Streaming/Channels/602',
            'rtsp://vctech:Vctech@1234@192.168.2.114:4345/Streaming/Channels/402',
            'rtsp://vctech:Vctech@1234@192.168.2.114:4345/Streaming/Channels/1002',
            'rtsp://vctech:Vctech@1234@192.168.2.114:4345/Streaming/Channels/802',
        ]
        return StreamingHttpResponse(gen(VideoCamera(sources[int(stream_id)-1:int(stream_id)])), content_type="multipart/x-mixed-replace;boundary=frame")
    except ValueError as e:
        return render(request, 'info/error.html', {'error_message': str(e)})



    # Optionally, you can customize the logout URL
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')  # Redirect to login page after logout

import requests
from django.shortcuts import render
from django.http import JsonResponse
from xml.etree import ElementTree as ET
from requests.auth import HTTPDigestAuth
import logging

logger = logging.getLogger(__name__)

def fetch_device_info(api_url):
    response = requests.get(api_url, auth=HTTPDigestAuth('admin', 'vct280620'))
    response.raise_for_status()  # Raise an error for bad status codes
    return response.text

def parse_xml(xml_data):
    tree = ET.ElementTree(ET.fromstring(xml_data))
    root = tree.getroot()
    namespaces = {'ns': 'http://www.hikvision.com/ver20/XMLSchema'}

    channels = []
    for channel in root.findall('ns:InputProxyChannel', namespaces):
        channel_data = {
            'id': channel.find('ns:id', namespaces).text if channel.find('ns:id', namespaces) is not None else 'N/A',
            'name': channel.find('ns:name', namespaces).text if channel.find('ns:name', namespaces) is not None else 'N/A',
            'proxyProtocol': channel.find('ns:proxyProtocol', namespaces).text if channel.find('ns:proxyProtocol', namespaces) is not None else 'N/A',
        }
        channels.append(channel_data)
    return channels

def ddashboard(request):
    try:
        api_url_1 = 'http://10.11.12.122:81/ISAPI/ContentMgmt/InputProxy/channels'
        api_url_2 = 'http://10.11.12.93:81/ISAPI/ContentMgmt/InputProxy/channels'

        xml_data_1 = fetch_device_info(api_url_1)
        xml_data_2 = fetch_device_info(api_url_2)

        data_1 = parse_xml(xml_data_1)
        data_2 = parse_xml(xml_data_2)

        combined_data = data_1 + data_2
        total_ids = len(combined_data)
        proxy_protocol = combined_data[0]['proxyProtocol'] if combined_data else 'N/A'
        logger.debug("Data fetched and parsed successfully.")
    except requests.exceptions.RequestException as e:
        logger.error('Error fetching device info: %s', e)
        combined_data = []
        total_ids = 0
        proxy_protocol = 'N/A'

    return render(request, 'charts.html', {'device_info': combined_data, 'total_ids': total_ids, 'proxy_protocol': proxy_protocol})

def api_device_info(request):
    try:
        api_url_1 = 'http://10.11.12.122:81/ISAPI/ContentMgmt/InputProxy/channels'
        api_url_2 = 'http://10.11.12.93:81/ISAPI/ContentMgmt/InputProxy/channels'

        xml_data_1 = fetch_device_info(api_url_1)
        xml_data_2 = fetch_device_info(api_url_2)

        data_1 = parse_xml(xml_data_1)
        data_2 = parse_xml(xml_data_2)

        combined_data = data_1 + data_2
        total_ids = len(combined_data)
        proxy_protocol = combined_data[0]['proxyProtocol'] if combined_data else 'N/A'
        logger.debug("Data fetched and parsed successfully.")
    except requests.exceptions.RequestException as e:
        logger.error('Error fetching device info: %s', e)
        combined_data = []
        total_ids = 0
        proxy_protocol = 'N/A'

    return JsonResponse({'device_info': combined_data, 'total_ids': total_ids, 'proxy_protocol': proxy_protocol})





