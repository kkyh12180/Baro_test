import base64
from PIL import Image
from PIL.ExifTags import TAGS
from search.views import tokenizer, make_tokenizer
import os

def get_exif(file) :

    taglabel = {}

    # base64 데이터 저장
    content = file.read()
    image_binary = base64.b64encode(content).decode('UTF-8')
    taglabel['image_base64'] = image_binary

    # EXIF 추출
    image = Image.open(file)
    img_info = image._getexif()
    image.close()
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
        
        # prompt, negative tokenizer + 가중치
        prompt,neg_value = tokenizer(prompt,neg_value)
        prompt,neg_value = tokenizer(prompt,neg_value)
        
        taglabel["parameters"] = prompt
        taglabel["Negative prompt"] = neg_value

        # 기타 정보 작업
        etc_tmp = info_tmp[2].replace('\x00', '').strip().split('Hashes')[0].split(',')
        for etcs in etc_tmp :
            try :
                taglabel[etcs.strip().split(":")[0]] = etcs.strip().split(":")[1].strip()
            except :
                break

    # print(taglabel)
    '''
        제목, prompt, negative_prompt, 이미지 링크, steps, sampler, cfg_scale, seed, size, model_hash, clip_skip, denoising_strength, Timestamp
        TODO: EXIF 이미지 형식 깔끔하게 정리
        TODO: EXIF가 존재하지 않을 경우 웹에서 가져오는 코드 추가
        TODO: 웹에서 가져올 때 text 처리
        TODO: 문자열 처리 + 바이트 코드로 넘어가는 부분 수정
    '''
    return taglabel

def main() :
    get_exif()

if __name__ == "__main__" : 
    main()