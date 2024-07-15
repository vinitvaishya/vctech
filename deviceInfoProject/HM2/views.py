from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
import logging
import xmltodict
from requests.auth import HTTPDigestAuth
from HM1.models import Alert

logger = logging.getLogger(__name__)

@login_required
def alert_dashboard2(request):
    auth = HTTPDigestAuth('admin', 'vct280620')
    
    urls = {
        'device': 'http://10.11.12.93:81/ISAPI/System/deviceInfo?format=xml',
        'storage': 'http://10.11.12.93:81/ISAPI/ContentMgmt/Storage/hdd/capabilities?format=xml',
        'status': 'http://10.11.12.93:81/ISAPI/System/status?format=xml',
        'camera': 'http://10.11.12.93:81/ISAPI/ContentMgmt/InputProxy/channels?'
    }

    context = {key: None for key in urls.keys()}

    for key, url in urls.items():
        try:
            response = requests.get(url, auth=auth)
            response.raise_for_status()
            if response.content:
                data = xmltodict.parse(response.content)
                if key == 'storage':
                    context[key] = data.get('hddList', {}).get('hdd')
                elif key == 'camera':
                    context[key] = data.get('InputProxyChannelList', {}).get('InputProxyChannel')
                    # Check each camera status
                    if context[key]:
                        for channel in context[key]:
                            if not channel.get('sourceInputPortDescriptor', {}).get('serialNumber'):
                                Alert.objects.create(
                                    alert_type=key, 
                                    message=f"Camera {channel.get('id')} status abnormal.",
                                    source='HM2'
                                )
                else:
                    context[key] = data.get(next(iter(data)))
                logger.debug(f"{key.capitalize()} data retrieved successfully.")
        except requests.exceptions.RequestException as e:
            logger.error(f'{key.capitalize()} Info Request Exception: %s', e)
            Alert.objects.create(alert_type=key, message=f'{key.capitalize()} status abnormal.', source='HM2')

    return render(request, 'info/alert_dashboard.html', context)
