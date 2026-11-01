class DemandForecaster:
    """
    ML and Statistical Demand Analytics and Dynamic Pricing Engine for Administrators.
    """

    def analyze_treks(self, treks):
        if not treks:
            return {
                "overall_utilization": 0,
                "total_capacity": 0,
                "total_bookings": 0,
                "projected_revenue": 0.0,
                "treks_data": []
            }

        treks_data = []
        total_capacity = 0
        total_bookings = 0
        projected_revenue = 0.0

        for trek in treks:
            capacity = trek.max_participants or 1
            bookings_count = len(trek.bookings) if trek.bookings else 0
            fill_rate = min(100.0, round((bookings_count / capacity) * 100, 1))

            total_capacity += capacity
            total_bookings += bookings_count
            trek_revenue = bookings_count * (trek.price or 0.0)
            projected_revenue += trek_revenue

            # Classify Demand and Suggest Dynamic Pricing Optimization
            if fill_rate >= 80.0:
                demand_tier = "High Demand"
                demand_badge = "danger"
                rec_price_delta = "+10% to +15%"
                action_advice = "Trek is nearing capacity. Consider opening an additional batch or optimizing price."
            elif fill_rate >= 40.0:
                demand_tier = "Healthy Demand"
                demand_badge = "success"
                rec_price_delta = "Optimal (No Change)"
                action_advice = "Good booking velocity with steady participant enrollment."
            elif fill_rate > 0.0:
                demand_tier = "Moderate Demand"
                demand_badge = "info"
                rec_price_delta = "Hold / Seasonal Promo"
                action_advice = "Moderate interest. Recommend featuring in newsletter or social channels."
            else:
                demand_tier = "Low / Emerging"
                demand_badge = "secondary"
                rec_price_delta = "Promotional (-10%)"
                action_advice = "No bookings yet. Recommend early-bird discount or homepage highlight."

            treks_data.append({
                "id": trek.id,
                "name": trek.name,
                "location": trek.location,
                "difficulty": trek.difficulty,
                "price": trek.price,
                "capacity": capacity,
                "bookings_count": bookings_count,
                "available_slots": max(0, capacity - bookings_count),
                "fill_rate": fill_rate,
                "revenue": trek_revenue,
                "demand_tier": demand_tier,
                "demand_badge": demand_badge,
                "rec_price_delta": rec_price_delta,
                "action_advice": action_advice
            })

        overall_utilization = round((total_bookings / max(1, total_capacity)) * 100, 1)

        # Sort treks by fill rate descending
        treks_data.sort(key=lambda x: x["fill_rate"], reverse=True)

        return {
            "overall_utilization": overall_utilization,
            "total_capacity": total_capacity,
            "total_bookings": total_bookings,
            "projected_revenue": projected_revenue,
            "treks_data": treks_data
        }


# Singleton forecaster instance
demand_forecaster = DemandForecaster()
