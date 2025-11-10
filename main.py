import yfinance as yf
import json

# Get ticker from user
ticker = input("Enter ticker symbol: ").strip().upper()

# Create stock object
stock = yf.Ticker(ticker)

# Initialize data structure
data = {
    'ticker': ticker,
    'companyInfo': {},
    'salesGrowth': [],
    'fcfGrowth': [],
    'grossMargins': [],
    'earningsSurprise': [],
    'shortInterest': {},
    'earningsDates': {}
}

# Get company info
stockInfo = stock.info
data['companyInfo'] = {
    'name': stockInfo.get('longName', 'N/A'),
    'price': stockInfo.get('currentPrice', 0),
    'marketCap': stockInfo.get('marketCap', 0),
    'sector': stockInfo.get('sector', 'N/A'),
    'industry': stockInfo.get('industry', 'N/A')
}

# ============================================================
# SALES GROWTH Y/Y (Last 3 Quarters)
# ============================================================
incomeStatement = stock.quarterly_income_stmt

if 'Total Revenue' in incomeStatement.index:
    allRevenue = incomeStatement.loc['Total Revenue']
    allRevenue = allRevenue.sort_index(ascending=False)

    for i in range(3):
        if i + 4 < len(allRevenue):
            currentQuarterRevenue = allRevenue.iloc[i]
            lastYearRevenue = allRevenue.iloc[i + 4]
            revenueChange = currentQuarterRevenue - lastYearRevenue
            growthPercentage = (revenueChange / abs(lastYearRevenue)) * 100
            quarterDate = allRevenue.index[i].strftime('%Y-%m-%d')

            data['salesGrowth'].append({
                'quarter': f'Q{i+1}',
                'date': quarterDate,
                'currentRevenue': float(currentQuarterRevenue),
                'lastYearRevenue': float(lastYearRevenue),
                'growth': round(growthPercentage, 2)
            })

# ============================================================
# FREE CASH FLOW GROWTH (Last 4 Quarters)
# ============================================================
cashflowStatement = stock.quarterly_cashflow

if 'Free Cash Flow' in cashflowStatement.index:
    allFcf = cashflowStatement.loc['Free Cash Flow']
    allFcf = allFcf.sort_index(ascending=False)

    for i in range(4):
        if i + 4 < len(allFcf):
            currentQuarterFcf = allFcf.iloc[i]
            lastYearFcf = allFcf.iloc[i + 4]
            fcfChange = currentQuarterFcf - lastYearFcf
            growthPercentage = (fcfChange / abs(lastYearFcf)) * 100

            data['fcfGrowth'].append({
                'quarter': f'Q{i+1}',
                'fcf': float(currentQuarterFcf),
                'growth': round(growthPercentage, 2)
            })

# ============================================================
# GROSS MARGINS (Last 4 Quarters)
# ============================================================
if 'Total Revenue' in incomeStatement.index and 'Gross Profit' in incomeStatement.index:
    allRevenue = incomeStatement.loc['Total Revenue']
    allGrossProfit = incomeStatement.loc['Gross Profit']
    allRevenue = allRevenue.sort_index(ascending=False)
    allGrossProfit = allGrossProfit.sort_index(ascending=False)

    for i in range(4):
        if i < len(allRevenue):
            quarterRevenue = allRevenue.iloc[i]
            quarterGrossProfit = allGrossProfit.iloc[i]
            grossMarginPercentage = (quarterGrossProfit / quarterRevenue) * 100

            data['grossMargins'].append({
                'quarter': f'Q{i+1}',
                'margin': round(grossMarginPercentage, 2)
            })

# ============================================================
# EARNINGS SURPRISE HISTORY
# ============================================================
earningsData = stock.earnings_dates

if earningsData is not None and not earningsData.empty:
    earningsData = earningsData.sort_index(ascending=False)
    earningsCount = 0

    for date, row in earningsData.iterrows():
        if earningsCount >= 4:
            break

        if 'Reported EPS' in row and 'EPS Estimate' in row:
            reportedEps = row['Reported EPS']
            estimatedEps = row['EPS Estimate']

            if reportedEps == reportedEps and estimatedEps == estimatedEps:
                surpriseAmount = reportedEps - estimatedEps
                surprisePercentage = (surpriseAmount / abs(estimatedEps)) * 100 if estimatedEps != 0 else 0
                dateString = date.strftime('%Y-%m-%d')

                data['earningsSurprise'].append({
                    'date': dateString,
                    'reportedEps': round(float(reportedEps), 2),
                    'estimatedEps': round(float(estimatedEps), 2),
                    'surprise': round(surprisePercentage, 2)
                })

                earningsCount += 1

# ============================================================
# SHORT INTEREST
# ============================================================
data['shortInterest'] = {
    'shortPercentOfFloat': round(stockInfo.get('shortPercentOfFloat', 0) * 100, 2) if stockInfo.get('shortPercentOfFloat') else 'N/A',
    'sharesShort': stockInfo.get('sharesShort', 'N/A'),
    'daysToCover': stockInfo.get('shortRatio', 'N/A')
}

# ============================================================
# EARNINGS DATES
# ============================================================
if earningsData is not None:
    # Find previous earnings date
    for date, row in earningsData.iterrows():
        if 'Reported EPS' in row:
            reported = row['Reported EPS']
            if reported == reported:
                data['earningsDates']['previous'] = date.strftime('%Y-%m-%d')
                break

    # Find next earnings date
    for date, row in earningsData.iterrows():
        if 'Reported EPS' in row:
            reported = row['Reported EPS']
            if reported != reported:
                data['earningsDates']['next'] = date.strftime('%Y-%m-%d')
                break

# Output JSON
print(json.dumps(data, indent=2))
