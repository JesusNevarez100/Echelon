from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from accounts.models import Membership
from accounts.services import get_primary_membership
from .forms import TaskForm, TaskInlineUpdateForm
from .models import Task

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

@method_decorator(login_required, name="dispatch")
class CRMIndexView(View):
    template_name = "crm/index.html"

    company_roles = {
        Membership.Role.ADMIN,
        Membership.Role.MANAGER,
        Membership.Role.STAFF,
    }

    client_roles = {
        Membership.Role.CLIENT,
    }

    def _get_membership(self, request):
        return get_primary_membership(request.user)
    
    def _get_base_tasks(self, membership):
        return Task.objects.filter(
            company=membership.company
        ).select_related(
            "assigned_to",
            "created_by",
            "contact",
            "service_request"
        )
    
    def _get_visible_tasks(self, request, membership):
        tasks = self._get_base_tasks(membership)

        if membership.role == Membership.Role.CLIENT:
            tasks = tasks.filter(assigned_to=request.user)
    
        return tasks.order_by("status", "due_at", "-created_at")
    
    def _get_my_tasks(self, request, membership):
        return self._get_base_tasks(membership).filter(
            assigned_to=request.user
        ).order_by("status", "due_at", "-created_at")
    
    def get(self, request, *args, **kwargs):
        membership = self._get_membership(request)

        if membership is None:
            return HttpResponseForbidden("No company membership recognized.")
        
        tasks = self._get_visible_tasks(request, membership)
        my_tasks = self._get_my_tasks(request, membership)

        return render(request, self.template_name, {
            "membership":membership,
            "tasks": tasks,
            "my_tasks": my_tasks,
            "can_create_tasks": _can_create_tasks(membership),
            "can_delete_tasks": _can_delete_task(membership),
            "task_status_choices": Task.Status.choices,
        })
    def post(self, request, *args, **kwargs):
        membership = self._get_membership(request)

        if membership is None:
            return HttpResponseForbidden("No company membership recognized.")
        
        action = request.POST.get("action")
        task_id = request.POST.get("task_id")

        if not task_id:
            return redirect("crm:index")
        
        task = get_object_or_404(
            Task,
            id=task_id,
            company=membership.company
        )

        if action == "update_status":
            if not _can_edit_task(request.user, membership, task):
                return HttpResponseForbidden("You do not have permission to update the status of this task.")
            
            new_status = request.POST.get("status")

            valid_statuses = [choice[0] for choice in Task.Status.choices]

            if new_status in valid_statuses:
                task.status = new_status
                task.save(update_fields=["status"])
            
        elif action == "update_task":
            if not _can_edit_task(request.user, membership, task):
                return HttpResponseForbidden("You do not have permission to edit this task")
            form = TaskInlineUpdateForm(
                request.POST,
                instance=task,
            )

            if form.is_valid():
                updated_task = form.save(commit=False)
                updated_task.company = membership.company

                # Do not allow users to change wo originally created the task
                updated_task.created_by = task.created_by
                
                # Clients can only keep tasks assigned to themselves
                if membership.role == Membership.Role.CLIENT:
                    updated_task.assigned_to = request.user
                
                updated_task.save()

        elif action == "deleted_task":
            if not _can_delete_task(membership):
                return HttpResponseForbidden("You do not have permission to delete this task.")
            
            task.delete()
        
        return redirect("crm:index")
    
index = CRMIndexView.as_view()
    
@login_required
def create_task(request):
    membership = get_primary_membership(request.user)
    if membership is None:
        return HttpResponseForbidden("No company membership recognized.")

    if not _can_create_tasks(membership):
        return HttpResponseForbidden("You do not have permission to create tasks.")
    company = membership.company

    task_instance = Task(
        company=company,
        created_by=request.user,
        assigned_to=request.user if membership.role == Membership.Role.CLIENT else None,
    )

    if request.method == "POST":
        form = TaskForm(
            request.POST, 
            instance=task_instance, 
            membership=membership
        )
        if form.is_valid():
            task = form.save(commit=False)

            if membership.role == Membership.Role.CLIENT:
                task.assigned_to = request.user

            task.company = company
            task.created_by = request.user
            task.save()

            return redirect("crm:index")
    else:
        form = TaskForm(
            membership=membership,
            instance=task_instance
        )

    return render(request, "crm/create_task.html", {
        "form": form,
        "membership": membership,
    })