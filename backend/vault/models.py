from django.db import models
import hashlib

def user_directory_path(instance, filename):
    """Define the upload path for files."""
    return f'uploads/{filename}'

class File(models.Model):
    file = models.FileField(upload_to=user_directory_path)
    filename = models.CharField(max_length=255, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.BigIntegerField()
    file_hash = models.CharField(max_length=64)
    is_duplicate = models.BooleanField(default=False)
    original_file = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='duplicates'
    )

    class Meta:
        unique_together = ('file_hash', 'filename')  # Prevent exact same file+name combination

    def __str__(self):
        return self.filename

    @staticmethod
    def calculate_hash(file_bytes):
        """Generate SHA-256 hash for file content."""
        return hashlib.sha256(file_bytes).hexdigest()

    def save(self, *args, **kwargs):
        """Override save to calculate file hash and size before saving."""
        if not self.file_hash:
            self.file.seek(0)
            file_content = self.file.read()
            self.file_hash = self.calculate_hash(file_content)
            self.size = self.file.size
            self.file.seek(0)
        super().save(*args, **kwargs)
