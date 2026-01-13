import requests

def test_admin_finance():
    # 1. Login
    login_url = "http://127.0.0.1:5000/api/auth/login"
    login_data = {
        "email": "admin@spark.com",
        "password": "password123"
    }
    
    print(f"Logging in to {login_url}...")
    resp = requests.post(login_url, json=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code}")
        print(resp.text)
        return

    token = resp.json().get("access_token")
    print("Login successful.")

    # 2. Get Finance Riders
    finance_url = "http://127.0.0.1:5000/api/admin/finance/riders"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Fetching finance data from {finance_url}...")
    resp = requests.get(finance_url, headers=headers)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Data received: {len(data)} riders")
        for r in data:
            print(f"Rider: {r['email']}, Balance: {r['balance']}, Active Tasks: {r['active_tasks']}")
    else:
        print(f"Error: {resp.text}")

if __name__ == "__main__":
    test_admin_finance()
