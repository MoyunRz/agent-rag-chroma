from django.db import models


class Document(models.Model):
    kb = models.ForeignKey('knowledge.KnowledgeBase', on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=256)
    source_uri = models.CharField(max_length=512, blank=True)
    mime_type = models.CharField(max_length=64)
    file_path = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DocumentVersion(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        PROCESSING = 'processing'
        DONE = 'done'
        FAILED = 'failed'

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField(default=1)
    content_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    chunks_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['document', 'version_number']

    def __str__(self):
        return f'{self.document.title} v{self.version_number}'


class ChunkRecord(models.Model):
    version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    text = models.TextField()
    page = models.IntegerField(null=True, blank=True)
    heading_path = models.CharField(max_length=256, blank=True)
    content_hash = models.CharField(max_length=64)
    chroma_id = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chunk_index']
        unique_together = ['version', 'chunk_index']

    def __str__(self):
        return f'chunk #{self.chunk_index} of {self.version}'
