#!/usr/bin/env python3
import sys, asyncio, os, json, base64
sys.path.insert(0, 'src')
from brain.mcp_manager import mcp_manager
from brain.agents.grisha import Grisha

async def run():
    # Navigate and screenshot
    await mcp_manager.call_tool('puppeteer','puppeteer_navigate', {'url':'https://accounts.google.com/signup'})
    shot = await mcp_manager.call_tool('puppeteer','puppeteer_screenshot', {'name':'google_signup','encoded':False})
    image_data = None
    for c in shot.content:
        if getattr(c,'type','') == 'image':
            image_data = c.data
            break
    tf = None
    if image_data:
        tf = '/tmp/grisha_google_signup.png'
        with open(tf,'wb') as f:
            f.write(base64.b64decode(image_data))

    step = {'id':1, 'action':'Launch a browser and navigate to https://accounts.google.com/signup.','expected_result':'Browser window opens at the Google account signup page. (visual)'}
    result = {'success': True, 'output': 'Navigated to accounts.google.com/signup'}

    gr = Grisha()
    verification = await gr.verify_step(step, result, screenshot_path=tf)

    out = {'verified': bool(verification.verified), 'confidence': float(verification.confidence), 'description': verification.description}
    with open('/tmp/grisha_verification_result.json','w') as f:
        json.dump(out, f)

    await mcp_manager.cleanup()

if __name__ == '__main__':
    asyncio.run(run())
