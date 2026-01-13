from django.db import models

class FileTag(models.Model):
    file = models.ForeignKey('File', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('file', 'tag'),)
        verbose_name = "FileTag"
        verbose_name_plural = "FileTag"

    def __str__(self):
        return f"{self.file} - {self.tag}"
