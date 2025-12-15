import yfinance as yf


def get_yoy_last4(series):
    series = series.sort_index()
    return series.pct_change(periods=4).tail(4)


def metrics(ticker_symbol):
    t = yf.Ticker(ticker_symbol)

    # last 4 quarters FCF growth (y/y)
    try:
        fcf_growth_yoy = get_yoy_last4(t.quarterly_cashflow.loc["Free Cash Flow"])
    except KeyError:
        fcf_growth_yoy = None

    # last 4 quarters gross margin
    try:
        rev = t.quarterly_financials.loc["Total Revenue"].sort_index()
        gp = t.quarterly_financials.loc["Gross Profit"].sort_index()
        gm_last4 = (gp / rev).tail(4)
    except KeyError:
        gm_last4 = None

    q_earn = t.quarterly_earnings
    analysis = t.analysis

    sales_growth_next2 = None
    eps_growth_next2 = None

    if analysis is not None:
        if "Revenue Estimate" in analysis.index:
            rev_row = analysis.loc["Revenue Estimate"]
            sales_growth_next2 = {}
            for col in rev_row.index[:2]:
                ya_col = col + "-1Y"
                if ya_col in rev_row.index and rev_row[ya_col]:
                    sales_growth_next2[col] = rev_row[col] / rev_row[ya_col] - 1
                else:
                    sales_growth_next2[col] = None

        if "Earnings Estimate" in analysis.index:
            eps_row = analysis.loc["Earnings Estimate"]
            eps_growth_next2 = {}
            for col in eps_row.index[:2]:
                ya_col = col + "-1Y"
                if ya_col in eps_row.index and eps_row[ya_col]:
                    eps_growth_next2[col] = eps_row[col] / eps_row[ya_col] - 1
                else:
                    eps_growth_next2[col] = None

    info = t.get_info()
    short_keys = [
        "sharesShort",
        "sharesShortPriorMonth",
        "shortRatio",
        "shortPercentOfFloat",
    ]
    short_stats = {k: info.get(k) for k in short_keys}

    print(f"\n=== {ticker_symbol} metrics from yfinance ===")
    print("\nLast 4 quarters FCF YoY growth:")
    print(fcf_growth_yoy)
    print("\nLast 4 quarters Gross Margin:")
    print(gm_last4)
    print("\nQuarterly earnings (actual EPS & revenue):")
    print(q_earn)
    print("\nNext 2 quarters estimated SALES growth (y/y):")
    print(sales_growth_next2)
    print("\nNext 2 quarters estimated EPS growth (y/y):")
    print(eps_growth_next2)
    print("\nEarnings surprise history:")
    print("Not available from yfinance (no historical EPS estimate table).")
    print("\nShort interest stats (if available):")
    for k, v in short_stats.items():
        print(f"{k}: {v}")


def main():
    ticker_symbol = input("Enter your ticker (e.g. PLTR): ").upper()
    metrics(ticker_symbol)


if __name__ == "__main__":
    main()




