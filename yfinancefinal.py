import yfinance as yf
import json
import math
import sys

def clean_data(obj):
    if isinstance(obj, dict):
        return {k: clean_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj

def build_stock_report(ticker):
    stock = yf.Ticker(ticker)
    info = stock.get_info()

    data = {
        "ticker": ticker,
        "companyInfo": {},
        "salesGrowth": [],
        "fcfGrowth": [],
        "grossMargins": [],
        "earningsSurprise": [],
        "salesGrowthNext2": None,
        "epsGrowthNext2": None,
        "shortInterest": {},
        "earningsDates": {},
    }

    # Company info
    data["companyInfo"] = {
        "name": info.get("longName", "N/A"),
        "price": info.get("currentPrice"),
        "marketCap": info.get("marketCap"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }

    # Revenue growth YoY (last 3 quarters)
    try:
        rev = stock.quarterly_financials.loc["Total Revenue"]
        rev = rev.sort_index(ascending=False)

        for i in range(3):
            if i + 4 < len(rev):
                cur = rev.iloc[i]
                prev = rev.iloc[i + 4]
                growth = (cur - prev) / abs(prev) * 100

                data["salesGrowth"].append({
                    "quarter": f"Q{i+1}",
                    "date": rev.index[i].strftime("%Y-%m-%d"),
                    "currentRevenue": float(cur),
                    "lastYearRevenue": float(prev),
                    "growth": round(growth, 2),
                })
    except Exception:
        pass

    # Free cash flow growth YoY (last 4 quarters)
    try:
        fcf = stock.quarterly_cashflow.loc["Free Cash Flow"]
        fcf = fcf.sort_index(ascending=False)

        for i in range(4):
            if i + 4 < len(fcf):
                cur = fcf.iloc[i]
                prev = fcf.iloc[i + 4]
                growth = (cur - prev) / abs(prev) * 100

                data["fcfGrowth"].append({
                    "quarter": f"Q{i+1}",
                    "date": fcf.index[i].strftime("%Y-%m-%d"),
                    "fcf": float(cur),
                    "growth": round(growth, 2),
                })
    except Exception:
        pass

    # Gross margins (last 4 quarters)
 
    try:
        gp = stock.quarterly_financials.loc["Gross Profit"]
        rev = stock.quarterly_financials.loc["Total Revenue"]

        gp = gp.sort_index(ascending=False)
        rev = rev.sort_index(ascending=False)

        for i in range(4):
            margin = gp.iloc[i] / rev.iloc[i] * 100
            data["grossMargins"].append({
                "quarter": f"Q{i+1}",
                "margin": round(margin, 2),
            })
    except Exception:
        pass

    # Earnings surprise history (last 4)
    earnings = stock.earnings_dates
    if earnings is not None and not earnings.empty:
        earnings = earnings.sort_index(ascending=False)
        count = 0

        for date, row in earnings.iterrows():
            if count >= 4:
                break

            rep = row.get("Reported EPS")
            est = row.get("EPS Estimate")

            if rep == rep and est == est:
                surprise = (rep - est) / abs(est) * 100 if est != 0 else 0
                data["earningsSurprise"].append({
                    "date": date.strftime("%Y-%m-%d"),
                    "reportedEps": round(float(rep), 2),
                    "estimatedEps": round(float(est), 2),
                    "surprise": round(surprise, 2),
                })
                count += 1

    # Forward growth estimates (next 2 quarters)
    analysis = stock.analysis

    if analysis is not None:
        def forward_growth(row, n=2):
            out = {}
            cols = [c for c in row.index if not c.endswith("-1Y")][:n]
            for c in cols:
                prev = f"{c}-1Y"
                out[c] = row[c] / row[prev] - 1 if prev in row and row[prev] else None
            return out

        if "Revenue Estimate" in analysis.index:
            data["salesGrowthNext2"] = forward_growth(
                analysis.loc["Revenue Estimate"]
            )

        if "Earnings Estimate" in analysis.index:
            data["epsGrowthNext2"] = forward_growth(
                analysis.loc["Earnings Estimate"]
            )


    # Short interest

    data["shortInterest"] = {
        "sharesShort": info.get("sharesShort"),
        "sharesShortPriorMonth": info.get("sharesShortPriorMonth"),
        "shortRatio": info.get("shortRatio"),
        "shortPercentOfFloat": (
            round(info["shortPercentOfFloat"] * 100, 2)
            if info.get("shortPercentOfFloat") else None
        ),
    }

    # Earnings dates (previous / next)

    if earnings is not None:
        for date, row in earnings.iterrows():
            if row.get("Reported EPS") == row.get("Reported EPS"):
                data["earningsDates"]["previous"] = date.strftime("%Y-%m-%d")
                break

        for date, row in earnings.iterrows():
            if row.get("Reported EPS") != row.get("Reported EPS"):
                data["earningsDates"]["next"] = date.strftime("%Y-%m-%d")
                break

    return clean_data(data)

# CLI entry point
def main():
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
    else:
        ticker = input("Enter ticker (e.g. AAPL): ").upper()

    report = build_stock_report(ticker)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()




