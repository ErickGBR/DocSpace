from django.db import models

class EspacioTrabajo(models.Model):
    title = models.CharField(max_length=255)
    bucked_path = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title