class MetricsCalculator:
    @staticmethod
    def compute(processed_records):
        """
        Calcula totales procesados, válidos vs inválidos, conteo por estado y sumas por moneda.
        """
        total = len(processed_records)
        valid_records = [r for r in processed_records if r["is_valid"]]
        invalid_records = [r for r in processed_records if not r["is_valid"]]

        status_counts = {"SUCCESS": 0, "FAILED": 0, "PENDING": 0, "INVALID": 0}
        totals_by_currency = {}

        for item in valid_records:
            tx = item["data"]
            st = tx["status"]
            curr = tx["currency"]
            amt = tx["amount"]

            status_counts[st] = status_counts.get(st, 0) + 1
            totals_by_currency[curr] = round(totals_by_currency.get(curr, 0.0) + amt, 2)

        status_counts["INVALID"] = len(invalid_records)

        return {
            "total_processed": total,
            "valid_count": len(valid_records),
            "invalid_count": len(invalid_records),
            "status_counts": status_counts,
            "totals_by_currency": totals_by_currency
        }