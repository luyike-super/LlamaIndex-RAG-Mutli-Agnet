from tortoise import fields
from tortoise.models import Model
from datetime import datetime

class BaseModel(Model):
    """基础模型类"""
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True

class Document(BaseModel):
    """文档模型"""
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    file_path = fields.CharField(max_length=255, null=True)
    file_type = fields.CharField(max_length=50, null=True)
    metadata = fields.JSONField(default={})
    
    class Meta:
        table = "documents"
    
    def __str__(self):
        return self.title

class Embedding(BaseModel):
    """嵌入向量模型"""
    document = fields.ForeignKeyField('models.Document', related_name='embeddings')
    vector = fields.BinaryField()
    model_name = fields.CharField(max_length=100)
    
    class Meta:
        table = "embeddings"
    
    def __str__(self):
        return f"{self.document.title} - {self.model_name}" 