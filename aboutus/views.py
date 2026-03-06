

# from django.shortcuts import render
# from .models import AboutUs

# def aboutus(request):
#     about = AboutUs.objects.first()
#     return render(request, "aboutus.html", {"about": about})




from django.shortcuts import render
from .models import AboutUs, TimelineEvent

def aboutus(request):
    about = AboutUs.objects.last()
    timeline = TimelineEvent.objects.all()

    return render(request, "aboutus.html", {
        "about": about,
        "timeline": timeline
    })
