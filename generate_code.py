import asyncio
import websockets
import json
import base64
from PIL import Image
import io

async def get_code_from_screenshot(screenshot_path: str, websocket_url: str = "ws://localhost:7001/generate-code"):
    # Convert image to base64
    with open(screenshot_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    image_data_url = f"data:image/png;base64,{encoded_string}"
    
    # Prepare the message matching the exact frontend payload structure
    message = {
        "image": image_data_url,
        "inputMode": "image",
        "generationType": "create",
        "generatedCodeConfig": "html_css",
        "codeGenerationModel": "claude-3-5-sonnet-20240620",
        "openAiApiKey": None,
        "openAiBaseURL": None,
        "anthropicApiKey": None,
        "screenshotOneApiKey": None,
        "isImageGenerationEnabled": True,
        "editorTheme": "cobalt",
        "isTermOfServiceAccepted": False
    }

    async with websockets.connect(websocket_url) as websocket:
        # Send the initial message
        await websocket.send(json.dumps(message))
        
        # Dictionary to store code chunks for each variant
        variants = {}
        completed_variants = set()
        
        # Receive the response
        while True:
            try:
                response = await websocket.recv()
                response_data = json.loads(response)
                
                msg_type = response_data.get("type")
                msg_value = response_data.get("value", "")
                variant_idx = response_data.get("variantIndex", 0)
                
                # Initialize variant if not exists
                if variant_idx not in variants:
                    variants[variant_idx] = ""
                
                # Handle different message types
                if msg_type == "status":
                    print(f"Status (variant {variant_idx}): {msg_value}")
                    if msg_value == "Code generation complete.":
                        completed_variants.add(variant_idx)
                elif msg_type == "chunk":
                    variants[variant_idx] += msg_value
                    
                elif msg_type == "setCode":
                    variants[variant_idx] = msg_value
                elif msg_type == "error":
                    print(f"Error received: {msg_value}")
                    raise Exception(f"Backend error: {msg_value}")
                
                # Check if we have received all variants
                if len(completed_variants) == 2:  # Backend sends 2 variants
                    break
                    
            except websockets.exceptions.ConnectionClosed:
                break
        
        # Return the first variant (or you could choose to return all variants)
        return variants.get(0, "")

# Example usage
async def main():
    #code = await get_code_from_screenshot("test-frontend.JPG")
    code = await get_code_from_screenshot("example-screen.png")
    with open("example.html", "w") as f:
        f.write(code)
    print("Generated code saved to example.html")

if __name__ == "__main__":
    asyncio.run(main())