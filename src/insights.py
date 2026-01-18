def generate_insights(df):
    insights = []

    total_days = len(df)
    drought_days = (df["risk"] == "Drought").sum()
    severe_days = (df["risk"] == "Severe Drought").sum()

    if severe_days > 0:
        insights.append(
            f"⚠️ Severe drought expected for {severe_days} out of {total_days} days."
        )

    if drought_days > total_days * 0.5:
        insights.append(
            "🚨 More than 50% of the forecast period shows drought conditions."
        )

    trend = df["predicted_gwl"].iloc[-1] - df["predicted_gwl"].iloc[0]
    if trend < 0:
        insights.append("📉 Groundwater levels are declining over time.")
    else:
        insights.append("📈 Groundwater levels show a stable or improving trend.")

    if not insights:
        insights.append("✅ Groundwater conditions appear stable.")

    return insights
def recommend_actions(worst_risk):
    if worst_risk == "Severe Drought":
        return [
            "🚱 Enforce groundwater extraction limits",
            "📢 Alert local authorities immediately",
            "💧 Promote emergency water conservation"
        ]

    if worst_risk == "Drought":
        return [
            "⚠️ Restrict non-essential water usage",
            "🌱 Encourage efficient irrigation practices"
        ]

    if worst_risk == "Warning":
        return [
            "🔍 Monitor groundwater levels closely",
            "💡 Promote water-saving awareness"
        ]

    return ["✅ No immediate action required"]
