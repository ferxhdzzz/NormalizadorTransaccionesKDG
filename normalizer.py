import json
import re
from datetime import datetime

class TransactionNormalizer:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def parse_amount(self, raw_amount, raw_currency=None):
        """Convierte montos (strings con $, €, comas o centavos) a float."""
        if raw_amount is None:
            return None, raw_currency
        
        detected_currency = raw_currency
        str_val = str(raw_amount).strip()

        # Detección de símbolo de moneda si viene pegado al monto (ej: €99,99)
        if "€" in str_val:
            detected_currency = "EUR"
            str_val = str_val.replace("€", "")
        elif "$" in str_val:
            detected_currency = "USD"
            str_val = str_val.replace("$", "")

        str_val = str_val.strip()

        # Caso: Montos en centavos enteros (ej: 10050 sin punto decimal)
        if isinstance(raw_amount, int) or (str_val.isdigit() and len(str_val) > 2 and "." not in str_val and "," not in str_val):
            return round(float(str_val) / 100.0, 2), detected_currency

        # Manejar coma decimal europea (99,99 -> 99.99)
        str_val = str_val.replace(",", ".")

        try:
            val = float(str_val)
            return round(val, 2), detected_currency
        except ValueError:
            return None, detected_currency

    def parse_timestamp(self, raw_date):
        """Convierte múltiples formatos de fecha a ISO-8601 UTC string."""
        if not raw_date:
            return None

        str_date = str(raw_date).strip()
        for fmt in self.config["date_formats"]:
            try:
                dt = datetime.strptime(str_date, fmt)
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue
        return None

    def normalize_status(self, raw_status):
        """Mapea variantes de estado a SUCCESS, FAILED o PENDING."""
        if not raw_status:
            return None
        key = str(raw_status).strip().lower()
        return self.config["status_mapping"].get(key, "UNKNOWN")

    def normalize(self, raw_tx):
        """Detecta fuente y mapea al esquema normalizado final."""
        # Detección de tipo/fuente según llaves presentes
        source = "Unknown"
        raw_id = raw_tx.get("id") or raw_tx.get("transaction_id") or raw_tx.get("ref")
        
        if "transaction_id" in raw_tx:
            source = "Gateway_B"
        elif "ref" in raw_tx:
            source = "Gateway_C"
        elif "id" in raw_tx:
            source = "Gateway_A"

        # Extracción inicial de campos
        raw_amt = raw_tx.get("amount") if "amount" in raw_tx else raw_tx.get("total")
        raw_curr = raw_tx.get("currency") or raw_tx.get("currency_code")
        raw_dt = raw_tx.get("timestamp") or raw_tx.get("created_at") or raw_tx.get("date")
        raw_st = raw_tx.get("status") or raw_tx.get("state") or raw_tx.get("result")

        # Transformaciones
        amount, curr_from_amt = self.parse_amount(raw_amt, raw_curr)
        final_currency = (curr_from_amt or raw_curr or "").upper()
        
        normalized = {
            "id": str(raw_id) if raw_id is not None else None,
            "amount": amount,
            "currency": final_currency,
            "timestamp": self.parse_timestamp(raw_dt),
            "status": self.normalize_status(raw_st),
            "source": source
        }
        return normalized