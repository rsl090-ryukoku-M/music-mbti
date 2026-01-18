from django.db import models
from django.contrib.auth.models import User

class SpotifyAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="spotify")
    spotify_user_id = models.CharField(max_length=64, unique=True)

    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DiagnosisResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="diagnoses")
    computed_at = models.DateTimeField(auto_now_add=True)

    energy_score = models.FloatField()
    mood_score = models.FloatField()
    texture_score = models.FloatField()
    explore_score = models.FloatField()

    type_code = models.CharField(max_length=8)         # 例: AbcD
    sample_track_ids = models.JSONField(default=list)  # spotify track id 3つ

