from django import forms
from django.forms import ModelForm
from images.models import ImagePost

'''
image_post_id = models.CharField(primary_key=True, max_length=10)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='image_post')
    thumbnail_image = models.TextField()
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    post_time = models.DateField(auto_now_add=True)
    like_number = models.IntegerField(blank=True, null=True)
    adult = models.BooleanField(default=False)
    subscribe_only = models.BooleanField(default=False)

    class Meta:
        db_table = 'image_post'
'''

class MultiImageField(forms.FileField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.attrs['multiple'] = True
        self.widget.attrs['accept'] = 'image/*'

class ImagePostCreationForm(ModelForm) :
    class Meta :
        model = ImagePost
        fields = ['title', 'content', 'images', 'adult', 'subscribe_only']

    images = MultiImageField()

class ExifForm(forms.Form) :
    prompt = forms.CharField(widget=forms.Textarea)
    negative_prompt = forms.CharField(widget=forms.Textarea)
    seed = forms.CharField(max_length=30)
    steps = forms.IntegerField()
    sampler = forms.CharField(max_length=30)
    cfg_scale = forms.FloatField()
    model_hash = forms.CharField(max_length=30)
    clip_skip = forms.IntegerField()
    denoising_strength = forms.FloatField()

    class Meta :
        fields = ['prompt', 'negative_prompt', 'seed', 'steps', 'sampler', 'cfg_scale', 'model_hash', 'clip_skip', 'denoising_strength']