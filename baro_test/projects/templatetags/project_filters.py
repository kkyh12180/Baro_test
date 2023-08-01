# templatetags/project_filters.py
from django import template
from django.shortcuts import get_object_or_404
from posts.models import Post
from projects.models import Project

register = template.Library()

@register.filter
def get_project_posts(context, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    return Post.objects.filter(project=project)
