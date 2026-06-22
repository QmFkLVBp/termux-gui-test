import subprocess
import re

def get_gateway():
    res = subprocess.run(['ip', 'route', 'show', 'default'], capture_output=True, text=True)
    match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', res.stdout)
    return match.group(1) if match else '192.168.1.1'

def scan_network():
    print("🔍 Сканування мережі за допомогою nmap...")
    try:
        # Ping-сканування всієї підмережі
        result = subprocess.run(['nmap', '-sn', '192.168.1.0/24'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        hosts = []
        current_ip = None
        for line in lines:
            # Шукаємо IP-адресу
            ip_match = re.search(r'Nmap scan report for (?:[\w.-]+ )?\(?(\d+\.\d+\.\d+\.\d+)\)?', line)
            if ip_match:
                current_ip = ip_match.group(1)
            
            # Шукаємо MAC-адресу та виробника
            mac_match = re.search(r'MAC Address: ([\w:]+) \(([^)]+)\)', line)
            if mac_match and current_ip:
                hosts.append({
                    'ip': current_ip,
                    'mac': mac_match.group(1),
                    'vendor': mac_match.group(2)
                })
                current_ip = None  # Скидаємо, щоб не дублювати
        
        return hosts
    except FileNotFoundError:
        print("❌ Помилка: встановіть nmap командою: pkg install nmap")
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
    print(f"└── 🏠 РОУТЕР (ШЛЮЗ): {gateway_ip}")
    
    if not other_hosts:
        print("    └── (Немає активних пристроїв)")
    else:
        for idx, host in enumerate(other_hosts):
            ip = host.get('ip', 'N/A')
            vendor = host.get('vendor', 'Невідомий')
            mac = host.get('mac', 'N/A')
            
            icon = "💻"
            if vendor and any(x in vendor.lower() for x in ['samsung', 'apple', 'xiaomi', 'huawei', 'google', 'oneplus']):
                icon = "📱"
            elif vendor and any(x in vendor.lower() for x in ['lg', 'sony', 'philips', 'sharp', 'tcl']):
                icon = "📺"
            elif vendor and any(x in vendor.lower() for x in ['canon', 'hp', 'epson', 'brother']):
                icon = "🖨️"
            
            prefix = "    ├── " if idx < len(other_hosts) - 1 else "    └── "
            
            print(f"{prefix} {icon} {ip}")
            print(f"    │   └── Виробник: {vendor}")
            print(f"    │   └── MAC: {mac}")
    
    print("="*50)
    print(f"📊 Всього знайдено пристроїв: {len(other_hosts)}")
    print("="*50)

if __name__ == "__main__":
    main()
