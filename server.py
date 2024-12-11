import fastapi
from fastapi import File, UploadFile
from datetime import datetime
import os
from groq import Groq
from dotenv import load_dotenv
import base64
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
load_dotenv(".env")

groq = os.getenv('Groq')

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ies-frontend.netlify.app"],  # React app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    print("Image Recieved")
    def encode_image(image_path):

        with open(image_path, "rb") as image_file:

            return base64.b64encode(image_file.read()).decode('utf-8')
    def interpret_image_with_groq(image_data, api_key):
        """
        Parameters:
        - image_binary: bytes, the binary content of the image file.
        - api_key: str, the API key to authenticate with the GROQ Vision API.
        
        Returns:
        - str: A description of the image content, or an error message if the request fails.
        """
        
        try:
            client = Groq(api_key=api_key)
        
            completion = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "interpret the image, provide a description of the content that is uploaded"
                            },
                            {
                                "type": "image_url",
                                "image_url": {

                                    "url": f"data:image/jpeg;base64,{image_data}",
                                }
                            }
                        ]
                    }
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            return completion.choices[0].message.content

        except Exception as e:
            return f"An error occurred: {str(e)}"
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    file_extension = os.path.splitext(file.filename)[1]
    
    new_filename = f"uploads/{timestamp}{file_extension}"
    
    with open(new_filename, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    print("image saved")
    response = interpret_image_with_groq(encode_image(new_filename),api_key=groq)
    os.remove(new_filename)
    print({"filename" : new_filename, "description" : response})
    return JSONResponse(
            status_code=200,
            content={"filename": new_filename, "description": response},
        )
