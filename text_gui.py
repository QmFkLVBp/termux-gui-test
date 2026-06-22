import subprocess
import re
import json

def get_gateway():
    # Дізнаємось IP роутера
    res = subprocess.run(['ip', 'route', 'show', 'default'], capture_output=True, text=True)
    match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', res.stdout)
    return match.group(1) if match else '192.168.1.1'

def scan_network():
    print("🔍 Сканування мережі (це швидко)...")
    try:
        # arp-scan видає JSON, щоб легко парсити
        result = subprocess.run(['arp-scan', '--local', '--format=json'], capture_output=True, text=True)
        data = json.loads(result.stdout)
        return data.get('hosts', [])
    except FileNotFoundError:
        print("❌ Помилка: встановіть arp-scan командою: pkg install arp-scan")
        return []
    except Exception as e:
        print(f"❌ Помилка сканування: {e}")
        return []

def main():
    gateway_ip = get_gateway()
    hosts = scan_network()
    
    if not hosts:
        return
    
    # Відділяємо роутер від інших
    other_hosts = [h for h in hosts if h.get('ip') != gateway_ip]
    
    print("\n" + "="*50)
    print("🌐 МЕРЕЖЕВЕ ДЕРЕВО")
    print("="*50)
    
    # Корінь - наш роутер
    print(f"└── 🏠 РОУТЕР (ШЛЮЗ): {gateway_ip}")
    
    if not other_hosts:
        print("    └── (Немає активних пристроїв)")
    else:
        # Малюємо гілки для кожного пристрою
        for idx, host in enumerate(other_hosts):
            ip = host.get('ip', 'N/A')
            vendor = host.get('vendor', 'Невідомий')
            mac = host.get('mac', 'N/A')
            
            # Вибираємо іконку за назвою виробника
            icon = "💻"  # комп'ютер за замовчуванням
            if vendor and any(x in vendor.lower() for x in ['samsung', 'apple', 'xiaomi', 'huawei', 'google', 'oneplus']):
                icon = "📱"  # телефон
            elif vendor and any(x in vendor.lower() for x in ['lg', 'sony', 'philips', 'sharp', 'tcl']):
                icon = "📺"  # телевізор
            elif vendor and any(x in vendor.lower() for x in ['canon', 'hp', 'epson', 'brother']):
                icon = "🖨️"  # принтер
            
            # Останній елемент малюємо з "└──", попередні з "├──"
            prefix = "    ├── " if idx < len(other_hosts) - 1 else "    └── "
            
            # Виводимо рядок
            print(f"{prefix} {icon} {ip}")
            print(f"    │   └── Виробник: {vendor}")
            print(f"    │   └── MAC: {mac}")
    
    print("="*50)
    print(f"📊 Всього знайдено пристроїв: {len(other_hosts)}")
    print("="*50)

if __name__ == "__main__":
    main()
