from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Membership
from accounts.services import get_primary_membership
from .forms import TaskForm
from .models import Task


def _create_task_for_client(membership):
    return membership.role in {

    }

def _can_create_tasks(membership):
    return membership.role in {
        Membership.Role.ADMIN,
        Membership.Role.MANAGER,
        Membership.Role.STAFF,
        Membership.Role.CLIENT
    }


def _can_edit_task(user, membership, task):
    if membership.role in {Membership.Role.ADMIN, Membership.Role.MANAGER}:
        return True

    if membership.role == Membership.Role.STAFF:
        return task.created_by_id == user.id or task.assigned_to_id == user.id

    return False


def _can_delete_task(membership):
    return membership.role in {
        Membership.Role.ADMIN,
        Membership.Role.MANAGER,
    }


@login_required
def index(request):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    tasks = Task.objects.filter(company=membership.company).select_related(
        "assigned_to",
        "created_by",
        "contact",
        "service_request",
    )

    if membership.role == Membership.Role.CLIENT:
        tasks = tasks.filter(assigned_to=request.user)

    my_tasks = tasks.filter(assigned_to=request.user).order_by("status", "due_at", "-created_at")
    all_tasks = tasks.order_by("status", "due_at", "-created_at")

    return render(request, "crm/index.html", {
        "membership": membership,
        "my_tasks": my_tasks,
        "tasks": all_tasks,
        "can_create_tasks": _can_create_tasks(membership),
    })


@login_required
def create_task(request):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    if not _can_create_tasks(membership):
        return HttpResponseForbidden("You do not have permission to create tasks.")
    company = membership.company
    # Permissions!
    # Clients can assign only to themselves
    # Companies staff can assign only to themselves or clients
    # Managers can assign to everyone
    if request.method == "POST":
        task_instance = Task(
            company=membership.company,
            created_by=request.user,
            assigned_to=request.user if membership.role == Membership.Role.CLIENT else None,
        )
        form = TaskForm(request.POST, instance=task_instance, membership=membership)
        if form.is_valid():
            task = form.save(commit=False)
            if membership == Membership.Role.CLIENT:
                task.assigned_to = request.user

            task.company = membership.company
            task.created_by = request.user
            task.save()
            return redirect("crm:index")
    else:
        task_instance = Task(
            company=membership.company,
            created_by=request.user,
            assigned_to=request.user if membership.role == Membership.Role.CLIENT else None,
        )
        form = TaskForm(membership=membership)
    

    
    # if request.method == "POST":
    #     form = TaskForm(request.POST, membership=membership)
    #     if form.is_valid():
    #         task = form.save(commit=False)
    #         task.company = membership.company
    #         task.created_by = request.user
    #         task.save()
    #         return redirect("crm:index")
    # else:
    #     form = TaskForm(membership=membership)

    return render(request, "crm/create_task.html", {
        "form": form,
        "membership": membership,
    })


@login_required
def task_detail(request, task_id):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    tasks = Task.objects.filter(company=membership.company).select_related(
        "assigned_to",
        "created_by",
        "contact",
        "service_request",
    )

    if membership.role == Membership.Role.CLIENT:
        tasks = tasks.filter(assigned_to=request.user)

    task = get_object_or_404(tasks, id=task_id)

    return render(request, "crm/task_detail.html", {
        "membership": membership,
        "task": task,
        "can_edit": _can_edit_task(request.user, membership, task),
        "can_delete": _can_delete_task(membership),
    })


@login_required
def edit_task(request, task_id):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    task = get_object_or_404(Task, id=task_id, company=membership.company)

    if not _can_edit_task(request.user, membership, task):
        return HttpResponseForbidden("You do not have permission to edit this task.")

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task, membership=membership)
        if form.is_valid():
            form.save()
            return redirect("crm:task_detail", task_id=task.id)
    else:
        form = TaskForm(instance=task, membership=membership)

    return render(request, "crm/edit_task.html", {
        "form": form,
        "task": task,
        "membership": membership,
    })


@login_required
def delete_task(request, task_id):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    if not _can_delete_task(membership):
        return HttpResponseForbidden("You do not have permission to delete tasks.")

    task = get_object_or_404(Task, id=task_id, company=membership.company)

    if request.method == "POST":
        task.delete()
        return redirect("crm:index")

    return render(request, "crm/delete_task.html", {
        "task": task,
        "membership": membership,
    })