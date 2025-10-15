from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(
        User,
        through='ProjectMembership', # Specify the intermediate model
        related_name='projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, related_name='created_projects', on_delete=models.CASCADE)
    
    def add_member(self, user, role):
        ProjectMembership.objects.create(project=self, user=user, role=role)

    def remove_member(self, user):
        ProjectMembership.objects.filter(project=self, user=user).delete()

    def is_member(self, user: User) -> bool:
        if self.owner == user:
            return True
        return self.projectmembership_set.filter(user=user).exists()

class ProjectMembership(models.Model):
    """Intermediate model to store the role of a user in a project."""
    class RoleChoices(models.TextChoices):
        OWNER = 'owner', 'Owner'
        RESEARCHER = 'researcher', 'Researcher'
        # Add other roles as needed
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    date_joined = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('project', 'user')
