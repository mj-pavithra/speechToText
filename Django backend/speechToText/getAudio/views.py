from django.http import JsonResponse
import time
import requests
from django.views.decorators.csrf import csrf_exempt
import cloudinary.uploader
import json
AudioSourceURL ="asc"

# Your Cloudinary configuration here (already set up in your provided code)
          
cloudinary.config( 
  cloud_name = "dvgs7xgih", 
  api_key = "481564122689345", 
  api_secret = "pJxtza2zwsvYQAPrXAlTLAhXEL0" 
)
@csrf_exempt
def get_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']

        # Upload the audio file directly to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                audio_file,
                resource_type = 'auto', # Automatically detect whether it's an image, video, or audio
                folder = 'audio_uploads', # Optional: Organize uploads into a folder
            )
            print("+++++++++++++++++++++++++++++")
            print("Upload successful:", upload_result)
            audio_url = upload_result.get('url')  # Get the URL of the uploaded file
            print("Audio URL:", audio_url)
            ResponceFromGladia = transcribe_audio(audio_url)
            print("ResponceFromGladia",ResponceFromGladia)
            # You might want to save this URL in your database, depending on your use case

            return ResponceFromGladia
        except Exception as e:
            print(".............................")
            print("Error uploading to Cloudinary:", e)
            return JsonResponse({'error': 'Failed to upload audio file'}, status=500)

    else:
        return JsonResponse({'error': 'No audio file found'}, status=400)

def make_fetch_request(url, headers, method='GET', data=None):
    if method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    else:
        response = requests.get(url, headers=headers)
    return response.json()

def transcribe_audio(audio_url):
    gladia_key = "a070c3eb-1b11-443d-9680-10e347a33e18"  # Use your actual Gladia API token
    audio_file_url = audio_url

    if not audio_file_url:
        return JsonResponse({'error': 'No audio file URL received'}, status=400)

    gladia_url = "https://api.gladia.io/v2/transcription/"
    headers = {
        "x-gladia-key": gladia_key,
        "Content-Type": "application/json"
    }

    try:
        print("- Sending audio file URL to Gladia AI...")
        request_data = {"audio_url": audio_file_url}
        initial_response = make_fetch_request(gladia_url, headers, 'POST', request_data)
        print("Initial response with Transcription ID:", initial_response)

        result_url = initial_response.get("result_url")
        if result_url:
            while True:
                print("Polling for results...")
                poll_response = make_fetch_request(result_url, headers)
                
                if poll_response.get("status") == "done":
                    print("- Transcription done.")
                    
                    # Here, instead of just printing, we prepare the data to be sent back
                    utterances_data = poll_response.get("result", {}).get("transcription", {}).get("utterances", [])
                    
                    # Prepare a list to hold our formatted utterances data
                    formatted_utterances = []
                    for utterance in utterances_data:
                        for word_info in utterance.get("words", []):
                            formatted_utterances.append({
                                "word": word_info.get('word'),
                                "start": word_info.get('start'),
                                "end": word_info.get('end'),
                                "confidence": word_info.get('confidence')
                            })
                    
                    # Return the transcription and the detailed utterances data
                    return JsonResponse({
                        'transcription': poll_response.get("result", {}).get("transcription", {}).get("full_transcript"),
                        'utterances': formatted_utterances
                    })
                else:
                    print("Transcription status:", poll_response.get("status"))
                time.sleep(1)
        else:
            return JsonResponse({'error': 'No result URL received from Gladia AI'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
