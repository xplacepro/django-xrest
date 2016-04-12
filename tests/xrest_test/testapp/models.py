from django.db import models


class TestModel(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()

    def to_json_dict(self):
        return {
            'title': self.title,
            'text': self.text,
            'pk': self.pk
        }