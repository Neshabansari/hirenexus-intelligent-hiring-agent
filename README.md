conda create -n lang3 python==3.11 -y

1. activate env lang3

2. pip install -r requirements.txt

3. run you project

streamlit run app.py



## This is for how to open the project correctly:
🔹 1️⃣ Open Anaconda Prompt (NOT VS Code)

👉 Start Menu → Anaconda Prompt

Paste this command there:
conda activate lang3


You should see:

(lang3)

🔹 2️⃣ Still in Anaconda Prompt

👉 Go to your project folder

Paste this:
cd C:\PROJECT_WORK\RECRUITMENT_AGENT


(Optional check)

dir

🔹 3️⃣ Still in Anaconda Prompt

👉 Open VS Code from here

Paste this:
code .


⚠️ This step is VERY IMPORTANT
(Do not open VS Code manually)

🔹 4️⃣ Now in VS Code

👉 Open Terminal → New Terminal

You should see:

(lang3) PS C:\PROJECT_WORK\RECRUITMENT_AGENT>

🔹 5️⃣ In VS Code Terminal

👉 Install dependencies

Paste this:
pip install -r requirements.txt

🔹 6️⃣ In VS Code Terminal

👉 Run the project

Paste this:
streamlit run app.py
