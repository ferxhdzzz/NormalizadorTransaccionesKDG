class TransactionValidator:
    def __init__(self, config_path="config.json"):
        import json
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def validate(self, tx):
        """
        Valida que la transacción cumpla con el esquema objetivo.
        Retorna (is_valid, list_of_errors).
        """
        errors = []

        if not tx.get("id"):
            errors.append("Falta ID o es nulo")
        
        if tx.get("amount") is None or tx.get("amount") <= 0:
            errors.append("Monto inválido o no numérico")

        if not tx.get("currency") or tx.get("currency") not in self.config["supported_currencies"]:
            errors.append(f"Moneda no soportada/inválida: {tx.get('currency')}")

        if not tx.get("timestamp"):
            errors.append("Formato de fecha/timestamp inválido")

        if tx.get("status") not in ["SUCCESS", "FAILED", "PENDING"]:
            errors.append(f"Estado desconocido o inválido: {tx.get('status')}")

        is_valid = len(errors) == 0
        return is_valid, errors