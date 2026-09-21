"""Mock 상관계수의 결측과 계산 불가를 명시적으로 구분한다."""
import math


def correlation(points):
    valid = [point for point in points if point.get('compliance_rate') is not None and point.get('sales_amount') is not None]
    result = {'r': None, 'reason': None, 'n': len(valid)}
    if len(valid) < 3:
        result['reason'] = 'insufficient_samples'
        return result
    xs = [float(point['compliance_rate']) for point in valid]
    ys = [float(point['sales_amount']) for point in valid]
    mean_x, mean_y = sum(xs) / len(xs), sum(ys) / len(ys)
    variance_x = sum((x - mean_x) ** 2 for x in xs)
    variance_y = sum((y - mean_y) ** 2 for y in ys)
    if variance_x == 0 or variance_y == 0:
        result['reason'] = 'zero_variance'
        return result
    value = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / math.sqrt(variance_x * variance_y)
    result['r'] = round(max(-1, min(1, value)), 4)
    return result
