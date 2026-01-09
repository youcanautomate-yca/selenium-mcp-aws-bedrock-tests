# 🤖 Selenium MCP AWS Bedrock Tests

**AI-Powered Browser Automation Framework**
This repository makes browser automation very simple by integrating Selenium Model Context Protocol(MCP) with AWS Bedrock, self-directing browser automation. Instead of writing complex test scripts, simply describe what you want automated and let AI handle the execution!

---

## Complete implementation video:
- https://youtu.be/67bi5PSiKAU

## 🎯 What Does This Project Do?

This project allows you to:
- ✅ Describe browser automation tasks in **plain English**
- ✅ Let **AWS Bedrock AI** intelligently decide how to execute them
- ✅ Use **MCP Selenium tools** to automate real browsers
- ✅ Get results without writing a single Selenium command
- ✅ Convert executions into **reusable Selenium tests**

### Example

Instead of writing Selenium code like this:
```python
driver = webdriver.Chrome()
driver.get("https://www.amazon.in")
search_box = driver.find_element(By.ID, "twotabsearchtextbox")
search_box.click()
search_box.send_keys("iphone 16")
# ... 50 more lines of code
```

You write a simple prompt:
```
Open Chrome, navigate to amazon.in, search for "iphone 16", 
click the first product, get the title, and close the browser
```

**The AI figures out all the details!** 🚀

---

## 📋 System Requirements

Before you start, ensure you have:

- **macOS, Linux, or Windows** with Terminal/Command Prompt
- **Python 3.10 or higher** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Chrome or Firefox browser** installed
- **AWS Account** with Bedrock access - [Create here](https://aws.amazon.com/)
- **~500MB disk space** for dependencies

---

## 🚀 Complete Setup Guide (Step-by-Step)

### Step 1️⃣: Verify Python Installation

Open Terminal/Command Prompt and run:
```bash
python --version
```

Expected output: `Python 3.10.x` or higher

**If not installed:**
- Go to https://www.python.org/downloads/
- Download Python 3.10 or higher
- Run the installer and **CHECK "Add Python to PATH"**

---

### Step 2️⃣: Verify Node.js Installation

```bash
node --version
npm --version
```

Expected output: `v18.x.x` or higher for both

**If not installed:**
- Go to https://nodejs.org/
- Download LTS version
- Run the installer

---

### Step 3️⃣: Clone or Download the Project

**Option A: Using Git (if you have Git installed)**
```bash
git clone https://github.com/youcanautomate-yca/selenium-mcp-aws-bedrock-tests.git
cd selenium-mcp-aws-bedrock-tests
```

**Option B: Manual Download**
1. Download the project as ZIP
2. Extract it to a folder
3. Open Terminal in that folder

---

### Step 4️⃣: Create Python Virtual Environment

A virtual environment keeps project dependencies isolated and clean.

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Success indicator:** Your terminal should show `(venv)` at the start of each line.

---

### Step 5️⃣: Install Python Dependencies

With virtual environment activated:
```bash
pip install -r requirements.txt
```

This installs:
- `selenium` - Browser automation
- `boto3` - AWS integration
- `python-dotenv` - Environment variables
- `httpx` - HTTP client for MCP communication

---

### Step 6️⃣: Install Node Dependencies

```bash
npm install
```

This installs:
- `@angiejones/mcp-selenium` - MCP Selenium tools wrapper

---

### Step 7️⃣: Set Up AWS Credentials

#### A. Create AWS Access Keys

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click **Users** → **your-username**
3. Go to **Security credentials** tab
4. Click **Create access key**
5. Choose **"Local code"** option
6. Copy the **Access Key ID** and **Secret Access Key**
   - ⚠️ **SAVE THESE SECURELY!** You won't see them again.

#### B. Configure Local AWS Credentials

**Option 1: Using .env file (Easiest for beginners)**

1. In the project folder, open `.env` file in a text editor
2. Replace the placeholder values:

```env
# AWS Configuration
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_HERE
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY_HERE

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Browser Configuration
BROWSER=chrome
HEADLESS=true
```

3. Save the file

**Option 2: Using AWS CLI (Advanced)**

```bash
# Install AWS CLI if needed
pip install awscli

# Configure
aws configure

# Enter your credentials when prompted
```

#### C. Verify AWS Access

```bash
# Test AWS credentials
python -c "import boto3; print(boto3.client('bedrock').list_foundation_models()['modelSummaries'][:1])"
```

If it works, you'll see model info. If not, check your credentials!

---

### Step 8️⃣: Start the MCP Selenium Server

The MCP server is the bridge between Python and Selenium tools.

Open a **new Terminal window** (keep the first one for running tests):

```bash
cd /path/to/selenium-mcp-aws-bedrock-tests

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Start the server
node mcp-selenium-server.js
```

You should see:
```
🚀 MCP Selenium SSE Server listening on http://localhost:8000
📞 POST /call endpoint available for JSON-RPC calls
```

**Leave this window open!** The server must keep running.

---

### Step 9️⃣: Test the Setup

In your **first Terminal window** (with Python venv activated), run:

```bash
python bedrock_browser_automation.py --prompt "Open Chrome and navigate to example.com, get the page title, and close the browser"
```

### Expected Output:

```
======================================================================
BEDROCK-DRIVEN MCP BROWSER AUTOMATION
======================================================================
MCP Server: http://localhost:8000
Bedrock Model: anthropic.claude-3-5-sonnet-20241022-v2:0
AWS Region: us-west-2
======================================================================

📞 Calling AWS Bedrock with current context...

🤖 Bedrock Response:
I'll help you execute those steps using the MCP Selenium tools...

🔧 Executing tool: start_browser
   ✓ Success: Browser started with session_id: chrome_1234567890

🔧 Executing tool: navigate
   ✓ Success: Navigated to https://example.com

🔧 Executing tool: get_element_text
   ✓ Success: Example Domain

🔧 Executing tool: close_session
   ✓ Success: Browser session closed

✅ Task complete!
```

**If successful:** 🎉 Your setup is complete!

**If you see errors:**
- ❌ "Connection refused" → MCP server not running (check Step 8)
- ❌ "Method not found" → AWS credentials issue (check Step 7)
- ❌ "Browser not found" → Chrome/Firefox not installed

---

## 📖 How to Use

### Basic Usage

Create a text file with your automation task:

**Example: `prompts/amazon_search.txt`**
```
Open Chrome and navigate to https://www.amazon.in
1. Find and click the search bar
2. Enter the text "laptop"
3. Wait for search results
4. Click on the first product
5. Get the page title
6. Close the browser
```

Run it:
```bash
python bedrock_browser_automation.py --prompt-file prompts/amazon_search.txt
```

### Direct Command

```bash
python bedrock_browser_automation.py --prompt "Open Chrome, go to Google.com, and get the page title"
```

### Save Results to File

```bash
python bedrock_browser_automation.py --prompt-file prompts/test.txt > results.txt 2>&1
```

---

## 🛠️ Available Tools Bedrock Can Use

The AI can automatically use these tools:

| Tool | Purpose |
|------|---------|
| `start_browser` | Open Chrome, Firefox, etc. |
| `close_session` | Close the browser |
| `navigate` | Go to a URL |
| `find_element` | Locate an element on the page |
| `click_element` | Click something |
| `send_keys` | Type text |
| `get_element_text` | Read text from page |
| `press_key` | Send keyboard keys (Enter, Tab, etc.) |
| `hover` | Move mouse over element |
| `take_screenshot` | Capture page screenshot |
| `drag_and_drop` | Drag and drop elements |
| `upload_file` | Upload files to the page |

Bedrock will choose the right tools automatically!

---

## 💡 Tips for Best Results

### 1. **Be Specific and Clear**
❌ Bad: "Click the button"
✅ Good: "Click the 'Add to Cart' button"

### 2. **Include Element Details**
✅ Include IDs, classes, or descriptions when you know them
```
Click the search button (id="search-submit")
```

### 3. **Number Your Steps**
```
1. Find the email input
2. Enter user@example.com
3. Click login button
4. Wait for dashboard to load
```

### 4. **Add Timeouts for Slow Pages**
```
Wait for results to load (timeout=15 seconds)
```

### 5. **Use Natural Language**
Bedrock understands human language, so write naturally:
```
Find the 'Add to Cart' button and click it
```

---

## 📁 Project Structure

```
selenium-mcp-aws-bedrock-tests/
├── bedrock_browser_automation.py    ← Main automation script
├── mcp-selenium-server.js           ← MCP server wrapper
├── src/
│   ├── bedrock.py                   ← AWS Bedrock integration
│   └── __init__.py
├── prompts/
│   ├── browser_automation.txt        ← Example prompts
├── requirements.txt                 ← Python dependencies
├── package.json                     ← Node.js dependencies
├── .env                            ← Your AWS credentials (KEEP SECRET!)
└── README.md                        ← This file
```

---

## 🔒 Security Important!

### ⚠️ NEVER commit `.env` to Git!

Your AWS credentials are in `.env`. Keep them safe:

```bash
# View .gitignore (already includes .env)
cat .gitignore
```

Should contain:
```
.env
.env.local
.venv/
venv/
```

---

## 🐛 Troubleshooting

### Problem: "Connection refused"
```
Error: ConnectionError: ('Connection aborted.', ...)
```
**Solution:**
1. Make sure MCP server is running (check second Terminal window)
2. Run: `node mcp-selenium-server.js`

---

### Problem: "ModuleNotFoundError: No module named 'selenium'"
```
ModuleNotFoundError: No module named 'selenium'
```
**Solution:**
1. Check virtual environment is activated `(venv)` shows at terminal start
2. Run: `pip install -r requirements.txt`

---

### Problem: "AWS credentials not found"
```
NoCredentialsError: Unable to locate credentials
```
**Solution:**
1. Check `.env` file has correct values
2. Verify you copied the access key and secret key correctly
3. Check AWS region is set to `us-west-2`

---

### Problem: "Browser not found"
```
WebDriverException: Unable to find the Chrome executable
```
**Solution:**
1. Install Chrome: https://www.google.com/chrome/
2. Or use Firefox: change `browser=firefox` in `.env`

---

### Problem: "Bedrock model not found"
```
ValidationException: Could not find a model
```
**Solution:**
1. Check your AWS region has Bedrock enabled
2. Go to https://console.aws.amazon.com/bedrock/
3. Verify you have access to Claude 3.5 Sonnet model

---

## 📞 Getting Help

1. **Check logs:** Run with verbose output
   ```bash
   python bedrock_browser_automation.py --prompt "Your prompt" 2>&1 | tee output.log
   ```

2. **Check AWS Console:** https://console.aws.amazon.com/bedrock/

3. **Verify Bedrock model access:**
   ```bash
   python -c "import boto3; client = boto3.client('bedrock'); print(client.list_foundation_models())"
   ```

---

## 🎓 Example Prompts

### Example 1: Wikipedia Search
```
Open Chrome and navigate to https://www.wikipedia.org
1. Find the search box
2. Search for "Artificial Intelligence"
3. Get the page title
4. Close the browser
```

### Example 2: GitHub Repository
```
Open Chrome and navigate to https://github.com/microsoft/vscode
1. Wait for page to load
2. Find the "Stars" count
3. Get the count value
4. Close the browser
```

### Example 3: Form Submission
```
Open Chrome and navigate to https://httpbin.org/forms/post
1. Fill in the form fields
2. Submit the form
3. Wait for response
4. Get the page title
5. Close the browser
```

---

## 🚀 Next Steps

1. ✅ Complete the setup (follow all steps above)
2. ✅ Run the test example to verify everything works
3. ✅ Create your own prompt in `prompts/` folder
4. ✅ Run your automation: `python bedrock_browser_automation.py --prompt-file prompts/your_prompt.txt`
5. ✅ Convert successful runs to reusable Selenium tests
6. ✅ Share your automations with your team!

---


## ✨ Features You Can Unlock

- 🤖 **AI-Driven Automation** - Let Bedrock figure out the best way
- 🔄 **Multi-Step Workflows** - Complex automations in plain English
- 📸 **Screenshots** - Automatic page captures
- ⌨️ **Keyboard Actions** - Press keys, type text
- 🖱️ **Mouse Actions** - Click, hover, drag-drop
- 📝 **Test Generation** - Convert automations to reusable tests
- 🔌 **MCP Integration** - Extensible tool framework

---

**Happy Automating! 🎉**
