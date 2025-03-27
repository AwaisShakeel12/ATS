from django.shortcuts import render, redirect
from .llm_model import get_gemini_response

import os 
from PIL import Image


import pdf2image
import io
import base64
import json

import google.generativeai as genai
from fpdf import FPDF
from .models import JobDescription

from .prompt2 import ats_analysis_prompt


from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
import google.generativeai as genai
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')
poppler_path =r'C:\Users\Awais Shakeel\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin'




def input_pdf_setup(upload_file):
    if upload_file is not None:
        # Convert PDF to image
        images = pdf2image.convert_from_bytes(upload_file.read(), poppler_path=poppler_path)
        first_page = images[0]
        
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                'mime_type': 'image/jpeg',
                'data': base64.b64encode(img_byte_arr).decode()
            }
        ]    
        return pdf_parts
    else:
        raise FileNotFoundError('No file uploaded')
    
    
    
def home(request):
    
    
    if request.method == 'POST':
        input_text = request.POST['input_text']
        upload_file = request.FILES.get('upload_file')
        
        job = JobDescription.objects.create(title=input_text, file=upload_file)
        job.save()
        return redirect('ats')
        
    return render(request , 'app/start.html')




        



import json





def ats(request):
    

    job = JobDescription.objects.last()
    file_path = job.file.path
    title = job.title

    with open(file_path, 'rb') as f:
        pdf_content = input_pdf_setup(f)

    try:
        response = get_gemini_response(title, pdf_content, ats_analysis_prompt)

        try_parsings = [
                response,
                response.strip(),  
                response.replace('```json', '').replace('```', '').strip(),
                response.split('```json')[-1].split('```')[0].strip(),  
        ]

        parsed_data = None
        for attempt in try_parsings:
            try:
                    parsed_data = json.loads(attempt)
                    break
            except json.JSONDecodeError:
                    continue

        if not parsed_data:
            raise json.JSONDecodeError("Could not parse JSON", response, 0)


        return render(request, 'app/home.html', {
                'score': parsed_data.get("score"),
                'review': parsed_data.get("review"),
                'full_review': parsed_data.get("full_review"),
                'spelling_mistakes': parsed_data.get("spelling_mistakes"),
                'quality_impact': parsed_data.get("quality_impact"),
                'missing_keywords': parsed_data.get("missing_keywords", []),
                'improvements': parsed_data.get("improvements", [])
        })

    except Exception as e:
        print(f"Error processing response: {e}")
        return render(request, 'app/home.html', {'error': f"Response processing error: {str(e)}"})

   






