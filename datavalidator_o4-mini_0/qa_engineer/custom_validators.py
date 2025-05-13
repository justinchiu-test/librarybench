def payment_limit_validator(limit):
    def validator(payload):
        errors = []
        amount = payload.get('amount')
        if isinstance(amount, (int, float)) and amount > limit:
            errors.append({
                'path': 'amount',
                'message': f'Amount exceeds limit of {limit}',
                'expected': f"<= {limit}",
                'actual': amount
            })
        return errors
    return validator
