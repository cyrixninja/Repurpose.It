from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()


def Image_Analysis(image_data):
    from azure.ai.vision.imageanalysis import ImageAnalysisClient
    from azure.ai.vision.imageanalysis.models import VisualFeatures
    from azure.core.credentials import AzureKeyCredential

    try:
        endpoint = os.getenv('VISION_ENDPOINT')
        key = os.getenv('VISION_KEY')
    except KeyError:
        print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create an Image Analysis client
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )


        
    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.CAPTION],
        language="en", 
    )

    print("Image analysis results:")
    # Print caption results to the console
    print(" Caption:")
    if result.caption is not None:
        print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")

    return result.caption.text

def Suggest_Use(Object):
    from openai import AzureOpenAI
    ENDPOINT = os.getenv('OPENAI_ENDPOINT')
    API_KEY = os.getenv('OPENAI_KEY')
    API_VERSION = "2024-02-01"
    MODEL_NAME = "gpt-4"
    client = AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version=API_VERSION,
    )
    MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "How can I repurpose or reuse following object :"+Object+" ?"},
    ]
    completion = client.chat.completions.create(
    model=MODEL_NAME,
    messages=MESSAGES,
    )
    print(completion.model_dump_json(indent=2))
    return completion.choices[0].message.content

# Tests
# Load image to analyze into a 'bytes' object
#with open("sample.jpg", "rb") as f:
#    image_data = f.read()
#Image_Analysis(image_data)


