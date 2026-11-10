import json
import os
from normalizer import TransactionNormalizer
from validator import TransactionValidator
from metrics import MetricsCalculator

class AppCLI:
    def __init__(self):
        self.normalizer = TransactionNormalizer()
        self.validator = TransactionValidator()
        self.records = [] # Guardará dicts: {"data": tx_norm, "is_valid": bool, "errors": list}

    def load_file(self, filepath):
        if not os.path.exists(filepath):
            print(f"❌ Error: El archivo '{filepath}' no existe.")
            return False
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            self.records = []
            for item in raw_data:
                norm_tx = self.normalizer.normalize(item)
                is_valid, errors = self.validator.validate(norm_tx)
                self.records.append({
                    "raw": item,
                    "data": norm_tx,
                    "is_valid": is_valid,
                    "errors": errors
                })
            print(f"✅ Archivo cargado exitosamente. {len(self.records)} registros procesados.")
            return True
        except Exception as e:
            print(f"❌ Error al leer el JSON: {e}")
            return False

    def display_metrics(self):
        if not self.records:
            print("⚠️ No hay datos cargados.")
            return

        metrics = MetricsCalculator.compute(self.records)
        print("\n" + "="*45)
        print("         📊 RESUMEN DE MÉTRICAS         ")
        print("="*45)
        print(f" Total procesadas : {metrics['total_processed']}")
        print(f" Transacciones Válidas   : {metrics['valid_count']}")
        print(f" Transacciones Inválidas : {metrics['invalid_count']}")
        print("-" * 45)
        print(" Conteo por Estado:")
        for st, count in metrics["status_counts"].items():
            print(f"   - {st}: {count}")
        print("-" * 45)
        print(" Totales de Monto por Moneda (Solo válidas):")
        for curr, total in metrics["totals_by_currency"].items():
            print(f"   - {curr}: {total:,.2f}")
        print("="*45 + "\n")

    def filter_records(self):
        if not self.records:
            print("⚠️ No hay datos cargados.")
            return

        print("\n--- 🔍 FILTRAR TRANSACCIONES ---")
        print("1. Ver todas las válidas")
        print("2. Ver todas las inválidas (con motivo)")
        print("3. Filtrar por Estado (SUCCESS, FAILED, PENDING)")
        print("4. Filtrar por Moneda (USD, EUR, etc.)")
        opt = input("Seleccione una opción: ").strip()

        filtered = []
        if opt == "1":
            filtered = [r for r in self.records if r["is_valid"]]
        elif opt == "2":
            filtered = [r for r in self.records if not r["is_valid"]]
        elif opt == "3":
            st_input = input("Ingrese estado (SUCCESS/FAILED/PENDING): ").strip().upper()
            filtered = [r for r in self.records if r["is_valid"] and r["data"]["status"] == st_input]
        elif opt == "4":
            curr_input = input("Ingrese moneda (USD/EUR): ").strip().upper()
            filtered = [r for r in self.records if r["is_valid"] and r["data"]["currency"] == curr_input]
        else:
            print("Opción inválida.")
            return

        print(f"\nMostrando {len(filtered)} resultados:")
        print("-" * 75)
        for idx, r in enumerate(filtered, 1):
            d = r["data"]
            if r["is_valid"]:
                print(f"{idx}. ID: {d['id']} | Monto: {d['amount']} {d['currency']} | Estado: {d['status']} | Fecha: {d['timestamp']} | Fuente: {d['source']}")
            else:
                print(f"{idx}. [INVÁLIDA] Datos: {d} | Errores: {', '.join(r['errors'])}")
        print("-" * 75 + "\n")

    def run(self):
        # Auto-cargar datos si existe el archivo por defecto
        if os.path.exists("data_test.json"):
            self.load_file("data_test.json")

        while True:
            print("\n=== SISTEMA DE NORMALIZACIÓN DE TRANSACCIONES ===")
            print("1. Cargar / Recargar archivo JSON")
            print("2. Ver Métricas Generales")
            print("3. Explorar y Filtrar Transacciones")
            print("4. Salir")
            choice = input("Seleccione una opción (1-4): ").strip()

            if choice == "1":
                path = input("Ingrese la ruta del archivo JSON [default: data_test.json]: ").strip()
                if not path:
                    path = "data_test.json"
                self.load_file(path)
            elif choice == "2":
                self.display_metrics()
            elif choice == "3":
                self.filter_records()
            elif choice == "4":
                print("¡Hasta luego!")
                break
            else:
                print("Opción inválida, intente de nuevo.")

if __name__ == "__main__":
    app = AppCLI()
    app.run()