# import openai

# # Set up your OpenAI API key
# api_key = "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"
# openai.api_key = api_key

# # Define your prompt
# prompt = "man riding horse on the moon and make it realistic"
# print("settt")
# # Call the OpenAI API to generate the image
# response = openai.Image.create(prompt=prompt,response_format="url")

# # Get the image URL from the response
# image_url = response['data'][0]['url']
# print(image_url)

# # You can now display the image using any library you prefer, like PIL or matplotlib
# # For example, using PIL
# from PIL import Image
# import requests
# from io import BytesIO

# image_data = requests.get(image_url).content
# image = Image.open(BytesIO(image_data))
# image.show()
import requests

url = "http://localhost:8000/docChat"

image = {'image': open('sample.png', 'rb')}
#payload ={"languages": ["en", "hi"]}  # send languages as separate items
payload ={"languages": "en, hi"}  # send languages as a single item
resp = requests.post(url=url, data=payload, files=image) 
print(resp.json())
