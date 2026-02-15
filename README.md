# ✅ EASIEST FIX (No Python Change Required)

### Step 1 — Edit `requirements.txt`

Remove this line completely:

```
torch==2.2.2+cpu --index-url https://download.pytorch.org/whl/cpu
```

Leave only:

```
sentence-transformers==5.2.2
```

Save file.

---

### Step 2 — Recreate clean venv (recommended)

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

---

### Step 3 — Install CPU Torch FIRST

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Let pip choose correct compatible version automatically.

It will install something like:

```
torch-2.x.x (CPU only)
```

Size ~200–300MB.

No CUDA.
No NVIDIA packages.

---

### Step 4 — Now Install Remaining Requirements

```bash
pip install -r requirements.txt
```

Now it will NOT try to reinstall GPU torch.

---

# 🧠 Why This Works

Because:

* sentence-transformers depends on torch
* If torch is already installed, pip will NOT install a new one
* So it won’t pull CUDA

---

# 🚀 Alternative (Even Simpler)

If you don’t care about CPU-only and just want it working:

Just delete the torch line completely and run:

```bash
pip install -r requirements.txt
```

Let it install the big CUDA build.

It will work.
Just heavy.

No error.

---

# 🎯 Your Situation

You are:

* Running locally
* Lenovo laptop
* Likely no NVIDIA GPU

So best option = CPU torch method above.

---

# 🧪 Quick Check After Install

After everything installs:

```bash
python
```

Then:

```python
import torch
print(torch.__version__)
print(torch.cuda.is_available())
```

It should print:

```
False
```

That means CPU-only build.

---

# 🧘 Final Clarity

There is **no system issue**.
There is **no OS issue**.
There is **no broken dependency**.

It is only:

> You pinned a torch version that does not exist for Python 3.12.

---
