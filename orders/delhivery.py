import requests
import json
from django.utils import timezone
import datetime
from django.conf import settings

def generate_waybill():
    url = f"{settings.DELHIVERY_BASE_URL}/waybill/api/bulk/json/"
    headers = {
        "Authorization": f"Token {settings.DELHIVERY_API_TOKEN}"
    }
    params = {"count": 1}

    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()

    waybill_text = res.text.strip()
    if "," in waybill_text:
        return waybill_text.split(",")[0]

    return waybill_text

def create_shipment(order):
    waybill = generate_waybill().strip('"')

    address = order.address

    # 🔴 COD vs Prepaid
    if order.payment_method == "COD":
        payment_mode = "COD"
        cod_amount = float(order.total_amount)
    else:
        payment_mode = "Prepaid"
        cod_amount = 0

    payload = {
        "shipments": [{
            "name": address.fullname,
            "phone": address.mobile,
            "address": f"{address.address1}, {address.address2 or ''}, {address.landmark or ''}",
            "city": address.city,
            "state": address.state,
            "pin": address.pincode,
            "country": address.country,
            "order": order.order_code,
            "payment_mode": payment_mode,
            "cod_amount": cod_amount,
            "total_amount": float(order.total_amount),
            "quantity": sum(item.quantity for item in order.items.all()),
            "products_desc": ", ".join(
                item.product.name for item in order.items.all()
            ),
            "weight": 0.5
        }]
    }

    headers = {
        "Authorization": f"Token {settings.DELHIVERY_API_TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{settings.DELHIVERY_BASE_URL}/api/cmu/create.json"
    res = requests.post(url, json=payload, headers=headers)
    res.raise_for_status()

    order.tracking_id = waybill
    order.courier_name = "Delhivery"
    order.shipment_created_at = timezone.now()
    order.save(update_fields=["tracking_id", "courier_name", "shipment_created_at"])

    return waybill

def request_pickup(order):
    import datetime

    url = f"{settings.DELHIVERY_BASE_URL}/fm/request/new/"

    headers = {
        "Authorization": f"Token {settings.DELHIVERY_API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "pickup_location": settings.DELHIVERY_PICKUP_LOCATION,
        "waybill": order.tracking_id,
        "pickup_date": datetime.date.today().isoformat()
    }

    print("Pickup request payload:", data)

    res = requests.post(url, json=data, headers=headers)

    if res.status_code != 200:
        print("Delhivery pickup error:", res.text)

    res.raise_for_status()
    return res.json()

def ship_order(order):
    if not order.tracking_id:
        create_shipment(order)

    # 🚫 Skip pickup in test mode
    if settings.DELHIVERY_MODE == "test":
        print("⚠️ Delhivery pickup skipped (TEST MODE)")
        return

    request_pickup(order)




#############


from django.utils import timezone
import uuid
from django.conf import settings

def create_return_shipment(return_request):
    """
    Creates a return shipment for a ReturnRequest.
    Works for TEST and LIVE mode.
    """

    if settings.DELHIVERY_MODE == "test":
        # -----------------------------
        # TEST MODE: simulate waybill and pickup
        # -----------------------------
        fake_waybill = "TEST-" + uuid.uuid4().hex[:8].upper()
        return_request.return_waybill = fake_waybill
        return_request.pickup_scheduled_at = timezone.now()
        return_request.status = "pickup_scheduled"
        return_request.save()

        print(f"⚠️ Return shipment simulated (TEST MODE) for ReturnRequest {return_request.id}")
        print(f"Waybill: {fake_waybill}, Pickup Scheduled At: {return_request.pickup_scheduled_at}")

        return fake_waybill

    else:
        # -----------------------------
        # LIVE MODE: actual Delhivery API call
        # -----------------------------
        from .delhivery import generate_waybill, request_pickup_by_waybill

        waybill = generate_waybill()
        return_request.return_waybill = waybill
        return_request.pickup_scheduled_at = timezone.now()
        return_request.status = "pickup_scheduled"
        return_request.save()

        # Trigger actual pickup via Delhivery API
        request_pickup_by_waybill(return_request)

        return waybill

def request_pickup_by_waybill(waybill: str):
    """
    Schedules pickup for a given waybill
    """

    if settings.DELHIVERY_MODE == "test":
        print("⚠️ Return pickup skipped (TEST MODE)")
        return

    url = "https://track.delhivery.com/fm/request/new/"

    headers = {
        "Authorization": f"Token {settings.DELHIVERY_API_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "waybill": waybill,
    }

    res = requests.post(url, json=data, headers=headers)

    if res.status_code != 200:
        print("❌ Delhivery return pickup error:", res.text)

    res.raise_for_status()



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import ReturnRequest
from orders.forms import ReturnPickupForm

# orders/delhivery.py
def schedule_delhivery_pickup(return_request):
    """
    Schedule Delhivery pickup for a ReturnRequest instance.
    Returns the generated waybill number.
    """
    from django.utils import timezone

    # Example: generate waybill
    waybill = f"WAYBILL-{return_request.id}"

    return_request.pickup_scheduled_at = timezone.now()
    return_request.status = "pickup_scheduled"
    return_request.return_waybill = waybill
    return_request.save()

    return waybill
