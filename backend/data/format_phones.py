import json
import re

def format_phone(phone_str):
    # Strip everything except digits
    digits = re.sub(r'\D', '', phone_str)
    
    # If it starts with 92, remove it for standard processing
    if digits.startswith('92'):
        digits = digits[2:]
    # If it starts with 0, remove it
    elif digits.startswith('0'):
        digits = digits[1:]
        
    # Now we should have exactly 10 digits for a Pakistani mobile number (e.g., 3001234567)
    # If not 10 digits, just return the original or try our best
    if len(digits) >= 10:
        digits = digits[-10:] # Take last 10
        return f"+92-{digits[:3]}-{digits[3:]}"
    return phone_str # Fallback

def main():
    file_path = 'c:/Users/Me/Desktop/Maahir/backend/data/mock_providers.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        providers = json.load(f)
        
    for p in providers:
        if 'phone' in p:
            old_phone = p['phone']
            new_phone = format_phone(old_phone)
            p['phone'] = new_phone
            
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(providers, f, indent=2, ensure_ascii=False)
        
    print(f"Updated {len(providers)} providers with formatted phone numbers.")

if __name__ == "__main__":
    main()
