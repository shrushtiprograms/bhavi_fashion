from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import TailorApplication


def tailor_jobs_form(request):
    """
    View for the tailor jobs application form
    """
    # Fetch all applications for the authenticated user
    applications = None
    if request.user.is_authenticated:
        applications = TailorApplication.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'tailor_jobs/tailor_jobs_form.html', {
        'applications': applications
    })


@login_required
def apply_for_job(request):
    """
    View to handle job application form submission
    """
    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        job_title = request.POST.get('job_title', 'Tailor Position')
        experience = request.POST.get('experience')
        work_mode = request.POST.get('work_mode')
        notes = request.POST.get('notes', '')

        # Handle skills (checkboxes)
        skills = request.POST.getlist('skills')
        skills_str = ','.join(skills)

        # Handle other skills
        other_skills = request.POST.get('other_skills', '')

        # Handle file upload
        sample_work = request.FILES.get('sample_work')

        # Create application record
        application = TailorApplication.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            address=address,
            job_title=job_title,
            experience=experience,
            skills=skills_str,
            other_skills=other_skills,
            work_mode=work_mode,
            sample_work=sample_work,
            notes=notes
        )

        messages.success(request, 'Your job application has been submitted successfully. We will contact you shortly.')
        return redirect('tailor_jobs:application_detail', application_id=application.id)

    # If not POST, redirect to the form
    return redirect('tailor_jobs:form')


@login_required
def application_detail(request, application_id):
    """
    View to display tailor application details
    """
    application = get_object_or_404(TailorApplication, id=application_id)

    # Check if the user is the owner of the application
    if application.user != request.user and not request.user.is_admin():
        return HttpResponseForbidden("You don't have permission to view this application")

    return render(request, 'tailor_jobs/application_detail.html', {
        'application': application
    })