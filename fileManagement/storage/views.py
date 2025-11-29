from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UploadedFile
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm
from django.db.models.functions import TruncDate
import datetime

@login_required
def dashboard(request):
    files = UploadedFile.objects.filter(user=request.user)
    return render(request, 'storage/dashboard.html', {'files': files})

@login_required
def upload_file(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        UploadedFile.objects.create(user=request.user, file=uploaded)
        return redirect('dashboard')
    return render(request, 'storage/upload.html')

@login_required
def delete_file(request, file_id):
    file_obj = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    file_obj.file.delete() #delete from disc
    file_obj.delete() #delete from database
    return redirect('dashboard')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request):
    #finds all the files uploaded by the user
    files = UploadedFile.objects.filter(user=request.user)

    #user statistics
    total_files = files.count()
    total_storage = sum(f.file.size for f in files) #in bytes
    most_recent = files.order_by('-uploaded_at').first() #sorts the files by the upload date and returns the latest one
     #for the upload streak
    today = datetime.date.today()
    streak = 0
    days = set(files.values_list('uploaded_at__date', flat=True))
    #makes a set of all unique upload dates

    while today - datetime.timedelta(days=streak) in days:
        streak += 1
    # checks to see if the user uploaded today, then the next day, then the next. and adds one to the streak count for every day

    uploads_per_day = (
        files.annotate(day=TruncDate('uploaded_at')) #extracts date
        .values('day') #group by date
        .annotate(count=Count('id')) #counts uploads on the day
        .order_by('day') #oldest to newest
    )

    #list of dates as strings + upload counts
    chart_labels = [item['day'].strftime('%Y-%m-%d') for item in uploads_per_day]
    chart_values = [item['count'] for item in uploads_per_day]

    #context for display
    context = {
        "total_files": total_files,
        "total_storage":round(total_storage / (1024 * 1024), 2),
        "most_recent": most_recent,
        "streak": streak,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
    }

    return render(request, "storage/profile.html", context)