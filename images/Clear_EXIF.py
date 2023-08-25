from PIL import Image
from PIL.ExifTags import TAGS

import os
import re
from urllib import parse

from search.models import Prompt

def get_exif(file) :
    taglabel = {}

    # EXIF 추출
    image = Image.open(file)
    img_info = image._getexif()

    # print(img_info)

    '''
    # 이미지 삭제
    os.remove(f'{IMG_TMP}/{image_num}.jpg')
    '''

    # EXIF 처리 부분
    info_tmp = []
    etc_tmp = []
    if (img_info is not None) :
        for tag, value in img_info.items() :
            if (type(value) is bytes) :
                dec_string = value.decode()
                dec_string = dec_string.replace('UNICODE', '').replace('"', '').replace('\x00', '')
                # print(dec_string)
                info_tmp = dec_string.split('\n')
    
        # prompt 넣어주기
        prompt = info_tmp[0].replace('\x00', '')

        # negative_prompt 넣어주기
        neg_value = info_tmp[1].split(':', 1)[1].replace('\x00', '').strip()
        
        taglabel["parameters"] = prompt
        taglabel["Negative prompt"] = neg_value
        
        # prompt, negative 가중치
        tokenizer(prompt,neg_value)
        
        # 기타 정보 작업
        etc_tmp = info_tmp[2].replace('\x00', '').strip().split('Hashes')[0].split(',')
        for etcs in etc_tmp :
            try :
                taglabel[etcs.strip().split(":")[0]] = etcs.strip().split(":")[1].strip()
            except :
                break

    # print(taglabel)
    
    return taglabel

def tokenizer(prompt,negative_prompt):
    #positive
    #<>를 제외한 모든 괄호를 제거하고 ','를 기준으로 분리
    prompt=re.sub(r'[-=+,#/\?:^.@*\"※~ㆍ!\'()\[\]{}]',',',prompt)
    prompt=prompt.replace('_',' ')
    tok = prompt.lower().split(',')

    for tk in tok:
        tk=make_tokenizer(tk)
        try:
            float(tk)
            continue
        except:
            if not tk:
                continue
            if "<" in tk or ">" in tk or tk=="lora":
                continue
        prompt = Prompt.objects.filter(prompt=tk)
        if not prompt:
            prompt=Prompt()
            prompt.prompt=tk
            prompt.positive_weight=2
            prompt.save()
        else:
            prompt_temp = prompt[0]
            prompt_temp.positive_weight=prompt_temp.positive_weight+2
            prompt_temp.save()

    #negative
    negative_prompt=re.sub(r'[-=+,#/\?:^.@*\"※~ㆍ!\'()\[\]{}]',',',negative_prompt)
    negative_prompt=negative_prompt.replace('_',' ')
    tok = negative_prompt.lower().split(',')
    for tk in tok:
        tk=make_tokenizer(tk)
        try:
            float(tk)
            continue
        except:
            if not tk:
                continue
            if "<" in tk or ">" in tk or tk=="lora":
                continue
        prompt = Prompt.objects.filter(prompt=tk)
        if not prompt:
            prompt=Prompt()
            prompt.prompt=tk
            prompt.negative_weight=2
            prompt.save()
        else:
            prompt_temp = prompt[0]
            prompt_temp.negative_weight=prompt_temp.negative_weight+2
            prompt_temp.save()

def make_tokenizer(tk):
    if ":" in tk:
        i=tk.find(":")
        tk=tk[:i]
    return tk.strip()

def main() :
    get_exif()

if __name__ == "__main__" : 
    main()