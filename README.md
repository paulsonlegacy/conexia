# **📜 conexia**  

A Python library for fetching and caching a device's real **public IP address** using STUN (Session Traversal Utilities for NAT) servers. Supports **Redis, SQLite, File-based, and In-Memory caching** for fast lookups.

📌 **Why Use This?**  
- Identifies real **public IP address** even behind NAT.  
- Provides **multiple cache backends** (Redis, SQLite, File, Memory).  
- **Works in Django, Flask, or standalone Python scripts**.
- Automatic caching capability with minimal configuration.

---

## **📦 Installation**  

```bash
pip install conexia
```

or install from source: 

```bash
git clone https://github.com/paulsonlegacy/conexia.git
cd conexia
pip install .
```

---

## **⚡ Usage**
### **Basic Example**
```python
from conexia.core import STUNClient

client = STUNClient()
stun_info = client.get_stun_info()
ip = client.get_public_ip()
port = client.get_public_port()
nat_type = client.get_nat_type()
print(f"STUN Info: {stun_info}")
print(f"Public IP: {ip}")
print(f"Public Port: {port}")
print(f"NAT Type: {nat_type}")
```
**Or run via command line after installation**
```
conexia
```

📌 **Output (Example)**  
```json
{
    "user_id": "device123",
    "data": {
        "ip": "192.168.1.10",
        "port": 3478,
        "nat_type": "Full Cone"
    },
    "timestamp": 1691234567
}
```

*NB - User ID is optional as it is automatically generated if not provided*

---

## **🔌 Integrating with Django**

1️⃣ Install the package

```bash
pip install conexia
```

2️⃣ Enable the STUN Middleware in settings.py 
Modify settings.py to activate the middleware and configure caching options:

```python
# settings.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    # ✅ Add Conexia Middleware
    "conexia.middleware.django.STUNMiddleware",
]

# STUN Configuration
STUN_CACHE_BACKEND = "sqlite"  # Options: "memory", "file", "sqlite", "redis"
STUN_CACHE_TTL = 300  # Cache expiry in seconds
```

3️⃣ Access STUN data inside Django Views 
Once the middleware is enabled, every request object will have the following attributes: 

```python
def sample_view(request):
    return JsonResponse({
        "original_ip": request.ip,
        "original_port": request.port,
        "nat_type": request.nat_type
    })
```

---

## **🌐 Integrating with Flask**

### 📌 Flask Integration Via Middleware

1️⃣ Install Flask and Conexia if you haven’t already

```bash
pip install flask conexia
```

2️⃣ Create app.py with the STUN middleware

```python
from flask import Flask, jsonify, g
from conexia.core import STUNClient
from stun_middleware import STUNMiddleware  # Import the middleware

app = Flask(__name__)

# Attach STUN Middleware with configurable options
STUNMiddleware(
    app, 
    cache_backend="redis",  # Change cache backend if needed (file, memory, etc.)
    ttl=300  # Set TTL for STUN data caching
)

@app.route("/get_ip")
def get_ip():
    return jsonify({
        "ip": g.get("ip"),
        "port": g.get("port"),
        "nat_type": g.get("nat_type"),
        "user_id": g.get("user_id")
    })

if __name__ == "__main__":
    app.run(debug=True)  # Runs synchronously with Flask's built-in server
```

3️⃣ Run the Server 
Run the application using Flask's built-in WSGI server:

```bash
python app.py
```

Flask will start at:

```bash
http://127.0.0.1:5000
```

4️⃣ Test API in Browser or Postman 
You can test the STUN attributes by making a request:

```bash
http://127.0.0.1:5000/get_ip
```

Example response:

```json
{
    "ip": "192.168.1.10",
    "port": "54321",
    "nat_type": "Symmetric NAT",
    "user_id": "device123"
}
```

### ✅ Alternative: Using Flask Hooks for STUN Info

If you prefer adding STUN information manually before each request, you can do:

```python
from flask import Flask, g, request
from conexia.core import STUNClient

app = Flask(__name__)
stun_client = STUNClient(backend="redis", ttl=300)

@app.before_request
def attach_stun_data():
    user_id = request.args.get("user_id", "default_id")
    stun_info = stun_client.get_stun_info(user_id)
    g.ip = stun_info['data']['ip']
    g.port = stun_info['data']['port']
    g.nat_type = stun_info['data']['nat_type']
    g.user_id = user_id  # Store user ID in Flask's request context

@app.route("/get_ip")
def get_ip():
    return jsonify({
        "ip": g.get("ip"),
        "port": g.get("port"),
        "nat_type": g.get("nat_type"),
        "user_id": g.get("user_id")
    })

if __name__ == "__main__":
    app.run(debug=True)
```

This approach attaches STUN data before every request without requiring custom middleware.

**Conclusion:** 

✅ Middleware automatically attaches STUN data 

✅ Flask hooks can be used as an alternative 

✅ Works natively with Flask (no async needed) 

---

## **💾 Available Cache Backends**

| Cache Backend | Description |
|--------------|------------|
| `memory` | Uses in-memory cache (Fast but not persistent). |
| `file` | Saves cached data in `cache.json` (Persistent across restarts). |
| `sqlite` | Uses an SQLite database for efficient storage. |
| `redis` | Uses Redis for distributed caching. |

NB - Default is *file*

---

## **🔧 Clearing Cache**

Clear cache for a specific user ID:  
```python
stun_client.clear_cache(user_id="device123")
```

Clear **all** cached data:

```python
stun_client.clear_cache()
```

---

## **📜 License**

This project is licensed under the MIT License.

---

## **👨‍💻 Contributing**

1️⃣ **Fork the repository**  
2️⃣ **Clone your fork**  

```bash
git clone https://github.com/paulsonlegacy/conexia.git
cd conexia
```

3️⃣ **Create a feature branch** 

```bash
git checkout -b feature-name
```

4️⃣ **Submit a pull request!** 🚀

---

## **🙌 Acknowledgments**

🎉 **This library is dedicated to my mom - Monica A. Bosah, whose support made this possible. And to Engr. Hussein Nasser to gave me the idea that birthed this library through his backend engineering course on Udemy** ❤️ 

---

## **🚀 Next Steps**

- [ ] Optional caching for simple tasks
- [ ] Support for synchronous and asynchronous for simplicity
- [ ] Add other network parameters in fetched stun info
- [ ] Stand-alone and environment simulated tests for middlewares
- [ ] Support for other python backend frameworks
- [ ] Signalling feature

---

### **💡 Want More Features?**

If you have feature suggestions or bugs, open an issue on **[GitHub](https://github.com/paulsonlegacy/conexia/issues)**! 🚀  
