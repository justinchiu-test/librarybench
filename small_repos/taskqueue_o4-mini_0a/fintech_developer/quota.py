class QuotaExceeded(Exception):
    pass

class QuotaManagement:
    def __init__(self, merchant_limit=1000, customer_limit=1000):
        self.merchant_limit = merchant_limit
        self.customer_limit = customer_limit
        self._merchant_usage = {}
        self._customer_usage = {}

    def check_and_consume(self, merchant_id, customer_id, amount):
        m_used = self._merchant_usage.get(merchant_id, 0)
        c_used = self._customer_usage.get(customer_id, 0)
        if m_used + amount > self.merchant_limit:
            raise QuotaExceeded(f"Merchant {merchant_id} quota exceeded")
        if c_used + amount > self.customer_limit:
            raise QuotaExceeded(f"Customer {customer_id} quota exceeded")
        self._merchant_usage[merchant_id] = m_used + amount
        self._customer_usage[customer_id] = c_used + amount

    def reset(self):
        self._merchant_usage.clear()
        self._customer_usage.clear()
