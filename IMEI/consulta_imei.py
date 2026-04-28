import sys
import re
import json
import urllib.request
import urllib.parse

def validar_imei(imei):
    imei = imei.strip().replace(" ", "").replace("-", "")
    if not re.fullmatch(r"\d{15}", imei):
        return None, "IMEI invalido: debe tener exactamente 15 digitos numericos."
    
    # Algoritmo de Luhn
    total = 0
    for i, d in enumerate(imei):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    if total % 10 != 0:
        return None, "IMEI invalido: fallo la verificacion de digito de control (Luhn)."
    
    return imei, None

def obtener_info_tac(imei):
    tac = imei[:8]
    print(f"\n[*] TAC (Type Allocation Code): {tac}")
    print(f"    Fabricante/modelo codificado en los primeros 8 digitos.")

    fabricantes = {
        "35": "Apple",
        "86": "Huawei",
        "35177": "Samsung",
        "35326": "Samsung",
        "86800": "Xiaomi",
        "86732": "OnePlus",
        "35403": "Nokia",
        "01": "AEG/Ericsson",
        "44": "Motorola",
    }
    for prefijo, marca in fabricantes.items():
        if tac.startswith(prefijo):
            print(f"    Posible fabricante: {marca}")
            break

def consultar_imeiinfo(imei):
    url = f"https://imeicheck.net/api/check?imei={imei}&service=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            print("\n[*] Resultado de imeicheck.net:")
            for k, v in data.items():
                print(f"    {k}: {v}")
    except Exception as e:
        print(f"\n[!] No se pudo consultar imeicheck.net: {e}")

def consultar_gsma(imei):
    print("\n[*] Para verificacion oficial GSMA (lista negra internacional):")
    print(f"    Visita: https://www.gsma.com/services/fraud-security/device-check/")
    print(f"    O: https://www.imei.info/?imei={imei}")

def mostrar_pasos_robo(imei):
    print("\n" + "="*55)
    print("  PASOS SI EL DISPOSITIVO FUE ROBADO O EXTRAVIADO")
    print("="*55)
    print(f"  1. Denuncia policial con IMEI: {imei}")
    print("  2. Contacta tu operador para BLOQUEAR el IMEI en red.")
    print("  3. Usa Find My Device (Android):")
    print("     https://www.google.com/android/find")
    print("  4. Usa Find My (iPhone):")
    print("     https://www.icloud.com/find")
    print("  5. Consulta lista negra nacional con tu operador.")

def main():
    print("=" * 55)
    print("       CONSULTA DE IMEI - imaGEO")
    print("=" * 55)

    if len(sys.argv) > 1:
        entrada = sys.argv[1]
    else:
        entrada = input("\nIngresa el numero IMEI (15 digitos): ").strip()

    imei, error = validar_imei(entrada)
    if error:
        print(f"\n[ERROR] {error}")
        sys.exit(1)

    print(f"\n[OK] IMEI valido: {imei}")
    obtener_info_tac(imei)
    consultar_imeiinfo(imei)
    consultar_gsma(imei)
    mostrar_pasos_robo(imei)
    print()

if __name__ == "__main__":
    main()
