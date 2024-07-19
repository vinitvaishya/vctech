from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
import logging
import xmltodict
from requests.auth import HTTPDigestAuth
from .models import Alert

logger = logging.getLogger(__name__)

@login_required
def alert_dashboard(request):
    auth = HTTPDigestAuth('vctech', 'Vctech@1234')
    
    urls = {
        'device': 'http://10.11.12.122:81/ISAPI/System/deviceInfo?format=xml',
       'storage': 'http://10.11.12.122:81/ISAPI/ContentMgmt/Storage/hdd/capabilities?format=xml',
        'status': 'http://10.11.12.122:81/ISAPI/System/status?format=xml',
        'camera': 'http://10.11.12.122:81/ISAPI/ContentMgmt/InputProxy/channels?'
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
                                    source='HM1'
                                )
                else:
                    context[key] = data.get(next(iter(data)))
                logger.debug(f"{key.capitalize()} data retrieved successfully.")
        except requests.exceptions.RequestException as e:
            logger.error(f'{key.capitalize()} Info Request Exception: %s', e)
            Alert.objects.create(alert_type=key, message=f'{key.capitalize()} status abnormal.', source='HM1')



    return render(request, 'info/alert_dashboard.html', context)







######



from django.shortcuts import render, redirect
from .models import Alert

def display_alerts(request):
    alerts = Alert.objects.filter(is_resolved=False).order_by('-created_at')  # Only fetch alerts that are not resolved
    return render(request, 'HM1/display_alerts.html', {'alerts': alerts})




from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .models import Alert  # Ensure this model is correctly defined and migrated

from django.shortcuts import redirect, get_object_or_404
from .models import Alert

from django.utils import timezone

def resolve_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    alert.resolve()
    return redirect('display_alerts')  # Make sure 'display_alerts' is the correct name for your view that displays alerts

def dismiss_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    alert.delete()
    return redirect('display_alerts')

def resolved_alerts(request):
    alerts = Alert.objects.filter(is_resolved=True)
    return render(request, 'HM1/resolved_alerts.html', {'alerts': alerts})

