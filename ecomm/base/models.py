from django.db import models
import uuid


#we don't want it to be a database table we want it to be only class---thatswhy abstract true
class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True , editable=False , default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now= True)
    updated_at = models.DateTimeField(auto_now_add= True)

    class Meta:
        abstract = True 



