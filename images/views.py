from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView, RedirectView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormMixin
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from images.models import ImagePost, ImageTable, ImagePrompt
from images.forms import ImagePostCreationForm, ExifForm
from images.Clear_EXIF import get_exif
from images.decorators import image_post_ownership_required
from comments.forms import CommentCreationForm
from follows.models import LikeImagePost, BookmarkImagePost

from synology_api import filestation

import string
import random
import os
# Create your views here.
IMG_URL = "https://vanecompany.synology.me/ai_image/image/"

@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class ImagePostCreateView(CreateView) :
    model = ImagePost
    form_class = ImagePostCreationForm
    template_name = 'images/create.html'
    
    # TODO 예외 처리 코드 필요
    def form_valid(self, form) :
        fl = filestation.FileStation('14.45.111.226', '5000', 'vane23', 'Syn_vane2023', secure=False, cert_verify=False, dsm_version=7, debug=True, otp_code=None)
        temp_post = form.save(commit=False)

        # UID 연결
        temp_post.user = self.request.user
        
        # IPID PK 처리
        ipid = ""
        while (True) :
            letters_set = string.ascii_letters
            num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
            random_list = random.sample(letters_set, num)
            random_str = f"I{''.join(random_list)}"

            try :
                ImagePost.objects.get(image_post_id=random_str)
            except :
                ipid = random_str
                break
        temp_post.image_post_id = ipid

        # 이미지 처리
        uploaded_images = self.request.FILES.getlist('images')
        
        # TODO 이미지 EXIF가 utf-8로 디코딩 되지 않을 때 처리 필요
        first_image_counter = 0

        for image in uploaded_images :
            new_image = ImageTable()
            new_prompt_pos = ImagePrompt()
            new_prompt_neg = ImagePrompt()

            # 이미지 키 생성
            pid = ""
            while (True) :
                letters_set = string.ascii_letters
                num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
                random_list = random.sample(letters_set, num)
                random_str = f"P{''.join(random_list)}"

                try :
                    ImageTable.objects.get(image_id=random_str)
                except :
                    pid = random_str
                    break

            # 이미지 업로드
            ext = image.name.split('.')[-1]
            image.name = f"{pid}.{ext}"
            path = default_storage.save(f"tmp/{image.name}", ContentFile(image.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)

            fl.upload_file(f"/web/ai_image/image", tmp_file)
            os.remove(tmp_file)

            taglabel = get_exif(image)
            # 이미지 처리
            new_image.image_id = pid
            new_image.user = self.request.user
            try : 
                new_image.image_file = f"{IMG_URL}{pid}.{ext}"
            except :
                pass
            try : 
                new_image.seed = taglabel['Seed']
            except :
                pass
            try : 
                new_image.steps = int(taglabel['Steps'])
            except :
                pass
            try : 
                new_image.sampler = taglabel['Sampler']
            except :
                pass
            try : 
                new_image.cfg_scale = float(taglabel['CFG scale'])
            except :
                pass
            try : 
                new_image.model_hash = taglabel['Model hash']
            except :
                pass
            try : 
                new_image.clip_skip = int(taglabel['Clip skip'])
            except :
                pass
            try : 
                new_image.denoising_strength = taglabel['Denoising strength']
            except :
                pass
            try : 
                new_image.adult = temp_post.adult
            except :
                pass

            # 썸네일 이미지 처리
            if (first_image_counter == 0) :
                temp_post.thumbnail_image = new_image.image_file
                temp_post.save()
                first_image_counter = first_image_counter + 1

            # 이미지 저장
            new_image.image_post_id = temp_post
            new_image.save()

            # 긍정 프롬프트 처리
            new_prompt_pos.image = new_image
            try :
                new_prompt_pos.prompt = taglabel['parameters']
            except :
                pass
            new_prompt_pos.is_positive = True

            # 부정 프롬프트 처리
            new_prompt_neg.image = new_image
            try :
                new_prompt_neg.prompt = taglabel['Negative prompt']
            except :
                pass
            new_prompt_neg.is_positive = False

            new_prompt_pos.save()
            new_prompt_neg.save()

        return super().form_valid(form)

    def get_success_url(self) : 
        return reverse('images:detail', kwargs={'pk': self.object.pk})

class ImagePostListView(ListView) :
    model = ImagePost
    context_object_name = 'image_post_list'
    template_name = 'images/list.html'
    paginate_by = 20
    
    def get_queryset(self):
        return ImagePost.objects.filter(subscribe_only=False,adult=False).order_by('-post_time')

class ImagePostDetailView(DetailView, FormMixin) :
    model = ImagePost
    form_class = CommentCreationForm
    context_object_name = 'target_post'
    template_name = 'images/detail.html'

    # 이미지 리스트 보내기
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)

        # 좋아요 정보 보내기
        image_post = self.object
        user = self.request.user

        if user.is_authenticated :
            likes = LikeImagePost.objects.filter(user=user, image_post=image_post)
            context['likes'] = likes
            bookmarks = BookmarkImagePost.objects.filter(user=user,image_post=image_post)
            context['bookmarks'] = bookmarks

        return context

@method_decorator(image_post_ownership_required, 'get')
@method_decorator(image_post_ownership_required, 'post')
class ImagePostDeleteView(DeleteView) :
    model = ImagePost
    context_object_name = 'target_post'
    template_name = 'images/detail.html'

    def get_success_url(self) :
        return reverse_lazy('images:list')

@method_decorator(image_post_ownership_required, 'get')
@method_decorator(image_post_ownership_required, 'post')
class ImagePostUpdateView(UpdateView) :
    model = ImagePost
    form_class = ImagePostCreationForm
    context_object_name = 'target_post'
    template_name = 'images/update.html'

    def form_valid(self, form) :
        fl = filestation.FileStation('14.45.111.226', '5000', 'vane23', 'Syn_vane2023', secure=False, cert_verify=False, dsm_version=7, debug=True, otp_code=None)
        temp_post = form.save(commit=False)
        ipid = temp_post.image_post_id

        # 기존 이미지 삭제 처리 필요
        #connected_images = ImageInPost.objects.filter(image_post=temp_post)
        # print(connected_images)

        #for connected_image in connected_images :
            #image = ImageTable.objects.get(image_id=connected_image.image.image_id)
            # print(image)
            #image.delete()
        
        # 이미지 처리
        uploaded_images = self.request.FILES.getlist('images')
        
        # TODO 이미지 EXIF가 utf-8로 디코딩 되지 않을 때 처리 필요
        first_image_counter = 0

        for image in uploaded_images :
            new_image = ImageTable()
            new_prompt_pos = ImagePrompt()
            new_prompt_neg = ImagePrompt()
            taglabel = get_exif(image)

            # 이미지 키 생성
            pid = ""
            while (True) :
                letters_set = string.ascii_letters
                num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
                random_list = random.sample(letters_set, num)
                random_str = f"P{''.join(random_list)}"

                try :
                    ImageTable.objects.get(image_id=random_str)
                except :
                    pid = random_str
                    break
            
            # 확장자명 가져오기
            ext = image.name.split('.')[-1]

            # 이미지 업로드
            new_name = f"{pid}.{ext}"
            new_file = SimpleUploadedFile(new_name, image.read(), content_type=image.content_type)
            fl.upload_file("/web/ai_image", new_file)

            # 이미지 처리
            new_image.image_id = pid
            new_image.user = self.request.user
            try : 
                new_image.image_file = f"{IMG_URL}{pid}.{ext}"
            except :
                pass
            try : 
                new_image.seed = taglabel['Seed']
            except :
                pass
            try : 
                new_image.steps = int(taglabel['Steps'])
            except :
                pass
            try : 
                new_image.sampler = taglabel['Sampler']
            except :
                pass
            try : 
                new_image.cfg_scale = float(taglabel['CFG scale'])
            except :
                pass
            try : 
                new_image.model_hash = taglabel['Model hash']
            except :
                pass
            try : 
                new_image.clip_skip = int(taglabel['Clip skip'])
            except :
                pass
            try : 
                new_image.denoising_strength = taglabel['Denoising strength']
            except :
                pass
            try : 
                new_image.adult = temp_post.adult
            except :
                pass

            # 썸네일 이미지 처리
            if (first_image_counter == 0) :
                temp_post.thumbnail_image = new_image.image_file
                temp_post.save()
                first_image_counter = first_image_counter + 1

            # 이미지 저장
            new_image.image_post_id = temp_post
            new_image.save()

            # FK를 위한 인스턴스 가져오기

            # 긍정 프롬프트 처리
            new_prompt_pos.image = new_image
            try :
                new_prompt_pos.prompt = taglabel['parameters']
            except :
                pass
            new_prompt_pos.is_positive = True

            # 부정 프롬프트 처리
            new_prompt_neg.image = new_image
            try :
                new_prompt_neg.prompt = taglabel['Negative prompt']
            except :
                pass
            new_prompt_neg.is_positive = False

            new_prompt_pos.save()
            new_prompt_neg.save()

        return super().form_valid(form)

    def get_success_url(self) :
        return reverse('images:detail', kwargs={'pk': self.object.pk})
    
class ImagePostLikeView(RedirectView) :
    def get_redirect_url(self, *args, **kwargs) :
        return reverse('images:detail', kwargs={'pk': self.request.GET.get('image_post_pk')})
    
    def get(self, request, *args, **kwargs) :
        image_post = get_object_or_404(ImagePost, pk=self.request.GET.get('image_post_pk'))
        user = self.request.user
        like = LikeImagePost.objects.filter(user=user, image_post=image_post)

        if like.exists() :
            image_post.like_number -= 1
            image_post.save()
            like.delete()
        else :
            image_post.like_number += 1
            image_post.save()
            LikeImagePost(user=user, image_post=image_post).save()

        return super(ImagePostLikeView, self).get(request, *args, **kwargs)

class ImagePostBookmarkView(RedirectView) :
    def get_redirect_url(self, *args, **kwargs) :
        return reverse('images:detail', kwargs={'pk': self.request.GET.get('image_post_pk')})
    
    def get(self, request, *args, **kwargs) :
        image_post = get_object_or_404(ImagePost, pk=self.request.GET.get('image_post_pk'))
        user = self.request.user
        like = BookmarkImagePost.objects.filter(user=user, image_post=image_post)

        if like.exists() :
            like.delete()
        else :
            BookmarkImagePost(user=user, image_post=image_post).save()

        return super(ImagePostBookmarkView, self).get(request, *args, **kwargs)

class ImagePostSubscribeView(RedirectView) :
    def get_redirect_url(self, *args, **kwargs) :
        return reverse('images:detail', kwargs={'pk': self.request.GET.get('image_post_pk')})
    
    def get(self, request, *args, **kwargs) :
        image_post = get_object_or_404(ImagePost, pk=self.request.GET.get('image_post_pk'))
        image_post.subscribe_only = not image_post.subscribe_only
        image_post.save()

        return super(ImagePostSubscribeView, self).get(request, *args, **kwargs)

class ImagePostAdultView(RedirectView) :
    def get_redirect_url(self, *args, **kwargs) :
        return reverse('images:detail', kwargs={'pk': self.request.GET.get('image_post_pk')})
    
    def get(self, request, *args, **kwargs) :
        image_post = get_object_or_404(ImagePost, pk=self.request.GET.get('image_post_pk'))
        image_post.adult = not image_post.adult
        image_post.save()

        return super(ImagePostAdultView, self).get(request, *args, **kwargs)

class InputExifInfo(FormView) :
    template_name = 'images/exif_info.html'
    form_class = ExifForm

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        pid = self.kwargs.get('pk')
        context['pid'] = pid

        return context
    
    def form_valid(self, form) :
        prompt = form.cleaned_data['prompt']
        negative_prompt = form.cleaned_data['negative_prompt']
        seed = form.cleaned_data['seed']
        steps = form.cleaned_data['steps']
        sampler = form.cleaned_data['sampler']
        cfg_scale = form.cleaned_data['cfg_scale']
        model_hash = form.cleaned_data['model_hash']
        clip_skip = form.cleaned_data['clip_skip']
        denoising_strength = form.cleaned_data['denoising_strength']

        image_id = self.kwargs.get('pk')

        # image 수정 저장
        image = ImageTable.objects.get(image_id=image_id)
        image.seed = seed
        image.steps = steps
        image.sampler = sampler
        image.cfg_scale = cfg_scale
        image.model_hash = model_hash
        image.clip_skip = clip_skip
        image.denoising_strength = denoising_strength
        image.save()

        # prompt 수정 저장
        pos_prom = ImagePrompt.objects.get(image=image, is_positive=True)
        pos_prom.prompt=prompt
        pos_prom.save()

        neg_prom = ImagePrompt.objects.get(image=image, is_positive=False)
        neg_prom.prompt=negative_prompt
        neg_prom.save()

        return super().form_valid(form)
    
    def get_success_url(self) :
        image = ImageTable.objects.get(image_id = self.kwargs.get('pk'))
        #ipid = ImageInPost.objects.get(image=image).image_post
        #return reverse('images:detail', kwargs={'pk': ipid.pk})