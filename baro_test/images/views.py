from typing import Any, Dict
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormMixin
from django.db import connection

from images.models import ImagePost, ImageTable, ImageInPost, ImagePrompt
from images.forms import ImagePostCreationForm
from images.Clear_EXIF import get_exif
from images.decorators import image_post_ownership_required
import string
import random
# Create your views here.

@method_decorator(login_required, 'get')
@method_decorator(login_required, 'post')
class ImagePostCreateView(CreateView) :
    model = ImagePost
    form_class = ImagePostCreationForm
    template_name = 'images/create.html'
    
    # TODO 예외 처리 코드 필요
    def form_valid(self, form) :
        temp_post = form.save(commit=False)

        # UID 연결
        temp_post.user = self.request.user
        
        # IPID PK 처리
        ipid = ""
        while (True) :
            letters_set = string.ascii_letters
            num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
            random_list = random.sample(letters_set, num)
            random_str = f"IP{''.join(random_list)}"

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
            new_image_in_post = ImageInPost()
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
            
            # 이미지 처리
            new_image.image_id = pid
            new_image.user = self.request.user
            try : 
                new_image.image_file = taglabel['image_base64']
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
                temp_post.thumbnail_image = taglabel['image_base64']
                temp_post.save()
                first_image_counter = first_image_counter + 1

            # 이미지 저장
            new_image.save()

            # FK를 위한 인스턴스 가져오기
            new_image_instance = ImageTable.objects.get(image_id=pid)
            new_image_post_instance = ImagePost.objects.get(image_post_id=ipid)
            # 긍정 프롬프트 처리
            new_prompt_pos.image = new_image_instance
            try :
                new_prompt_pos.prompt = taglabel['parameters']
            except :
                pass
            new_prompt_pos.is_positive = True

            # 부정 프롬프트 처리
            new_prompt_neg.image = new_image_instance
            try :
                new_prompt_neg.prompt = taglabel['Negative prompt']
            except :
                pass
            new_prompt_neg.is_positive = False
            
            new_image_in_post.image_post = new_image_post_instance
            new_image_in_post.image = new_image_instance

            new_prompt_pos.save()
            new_prompt_neg.save()
            new_image_in_post.save()

        return super().form_valid(form)

    def get_success_url(self) : 
        return reverse('images:detail', kwargs={'pk': self.object.pk})

class ImagePostListView(ListView) :
    model = ImagePost
    context_object_name = 'image_post_list'
    template_name = 'images/list.html'
    ordering = ['-post_time']
    paginate_by = 20

class ImagePostDetailView(DetailView) :
    model = ImagePost
    # form_class = CommentCreationForm
    context_object_name = 'target_post'
    template_name = 'images/detail.html'

    # 이미지 리스트 보내기
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        cursor = connection.cursor()

        ipid = self.kwargs.get('pk')

        post_list_sql = f'SELECT image_id FROM image_in_post WHERE image_post_id="{ipid}";'
        cursor.execute(post_list_sql)
        img_id_tuple = cursor.fetchall()
        # print(img_id_tuple)
        img_list = []

        first_img = 0
        for img_id in img_id_tuple :
            if (first_img == 0) :
                context['first_image'] = ImageTable.objects.get(image_id=img_id[0])
                first_img = first_img + 1
                continue
            img_list.append(ImageTable.objects.get(image_id=img_id[0]))
        context['image_list'] = img_list
        context['image_nums'] = list(range(0, len(img_list)))

        return context

@method_decorator(image_post_ownership_required, 'get')
@method_decorator(image_post_ownership_required, 'post')
class ImagePostDeleteView(DeleteView) :
    model = ImagePost
    context_object_name = 'target_post'
    template_name = 'images/delete.html'

    def get_success_url(self) :
        return reverse_lazy('images:list')

@method_decorator(image_post_ownership_required, 'get')
@method_decorator(image_post_ownership_required, 'post')
class ImagePostUpdateView(UpdateView) :
    model = ImagePost
    form_class = ImagePostCreationForm
    context_object_name = 'target_post'
    template_name = 'images/update.html'

    # TODO 수정 구현 필요
    '''
        기존 이미지 파일을 날리고, 새롭게 생성하는 로직으로 구성
    '''
    def form_valid(self, form) :
        temp_post = form.save(commit=False)
        ipid = temp_post.image_post_id

        # 기존 이미지 삭제 처리 필요
        connected_images = ImageInPost.objects.filter(image_post=temp_post)
        # print(connected_images)

        for connected_image in connected_images :
            image = ImageTable.objects.get(image_id=connected_image.image.image_id)
            print(image)
            image.delete()
        
        # 이미지 처리
        uploaded_images = self.request.FILES.getlist('images')
        
        # TODO 이미지 EXIF가 utf-8로 디코딩 되지 않을 때 처리 필요
        first_image_counter = 0

        for image in uploaded_images :
            new_image = ImageTable()
            new_prompt_pos = ImagePrompt()
            new_prompt_neg = ImagePrompt()
            new_image_in_post = ImageInPost()
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
            
            # 이미지 처리
            new_image.image_id = pid
            new_image.user = self.request.user
            try : 
                new_image.image_file = taglabel['image_base64']
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
                temp_post.thumbnail_image = taglabel['image_base64']
                temp_post.save()
                first_image_counter = first_image_counter + 1

            # 이미지 저장
            new_image.save()

            # FK를 위한 인스턴스 가져오기
            new_image_instance = ImageTable.objects.get(image_id=pid)
            new_image_post_instance = ImagePost.objects.get(image_post_id=ipid)
            # 긍정 프롬프트 처리
            new_prompt_pos.image = new_image_instance
            try :
                new_prompt_pos.prompt = taglabel['parameters']
            except :
                pass
            new_prompt_pos.is_positive = True

            # 부정 프롬프트 처리
            new_prompt_neg.image = new_image_instance
            try :
                new_prompt_neg.prompt = taglabel['Negative prompt']
            except :
                pass
            new_prompt_neg.is_positive = False
            
            new_image_in_post.image_post = new_image_post_instance
            new_image_in_post.image = new_image_instance

            new_prompt_pos.save()
            new_prompt_neg.save()
            new_image_in_post.save()

        return super().form_valid(form)

    def get_success_url(self) :
        return reverse('images:detail', kwargs={'pk': self.object.pk})