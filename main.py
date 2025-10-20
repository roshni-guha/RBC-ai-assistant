import yfinance as yf

# Get ticker from user
ticker = input("Enter ticker symbol: ").strip().upper()

# Create stock object
stock = yf.Ticker(ticker)

# Get company info
companyName = stock.info.get('longName', 'N/A')
currentPrice = stock.info.get('currentPrice', 'N/A')
marketCap = stock.info.get('marketCap', 0)

# Print company info
print(f"\n{'='*60}")
print(f"RESEARCH REPORT: {ticker}")
print(f"{'='*60}")
print(f"Company: {companyName}")
print(f"Price: ${currentPrice}")
print(f"Market Cap: ${marketCap:,.0f}")

# ============================================================
# SALES GROWTH Y/Y (Last 3 Quarters)
# ============================================================
print(f"\n{'='*60}")
print("SALES GROWTH Y/Y (Last 3 Quarters)")
print(f"{'='*60}")

# Get quarterly income statement data
incomeStatement = stock.quarterly_income_stmt

# Check if revenue data exists
if 'Total Revenue' in incomeStatement.index:
    # Get all revenue values
    allRevenue = incomeStatement.loc['Total Revenue']

    # Sort by date - most recent first
    allRevenue = allRevenue.sort_index(ascending=False)

    # Loop through last 3 quarters
    for i in range(3):
        # Check if we have enough data to compare year-over-year
        # We need data from 4 quarters ago (1 year ago)
        if i + 4 < len(allRevenue):
            # Get current quarter revenue
            currentQuarterRevenue = allRevenue.iloc[i]

            # Get revenue from same quarter last year (4 quarters ago)
            lastYearRevenue = allRevenue.iloc[i + 4]

            # Calculate year-over-year growth percentage
            revenueChange = currentQuarterRevenue - lastYearRevenue
            growthPercentage = (revenueChange / abs(lastYearRevenue)) * 100

            # Get the quarter date
            quarterDate = allRevenue.index[i].strftime('%Y-%m-%d')

            # Print results
            print(f"Quarter {i+1} ({quarterDate}):")
            print(f"  Current Revenue: ${currentQuarterRevenue:,.0f}")
            print(f"  Last Year Revenue: ${lastYearRevenue:,.0f}")
            print(f"  Y/Y Growth: {growthPercentage:.2f}%")
            print()

# ============================================================
# FREE CASH FLOW GROWTH (Last 4 Quarters)
# ============================================================
print(f"{'='*60}")
print("FREE CASH FLOW GROWTH (Last 4 Quarters)")
print(f"{'='*60}")

# Get quarterly cash flow data
cashflowStatement = stock.quarterly_cashflow

# Check if FCF data exists
if 'Free Cash Flow' in cashflowStatement.index:
    # Get all FCF values
    allFcf = cashflowStatement.loc['Free Cash Flow']

    # Sort by date - most recent first
    allFcf = allFcf.sort_index(ascending=False)

    # Loop through last 4 quarters
    for i in range(4):
        # Check if we have enough data to compare year-over-year
        if i + 4 < len(allFcf):
            # Get current quarter FCF
            currentQuarterFcf = allFcf.iloc[i]

            # Get FCF from same quarter last year
            lastYearFcf = allFcf.iloc[i + 4]

            # Calculate year-over-year growth
            fcfChange = currentQuarterFcf - lastYearFcf
            growthPercentage = (fcfChange / abs(lastYearFcf)) * 100

            # Print results
            print(f"Q{i+1}: ${currentQuarterFcf:,.0f} | Y/Y Growth: {growthPercentage:.2f}%")

# ============================================================
# GROSS MARGINS (Last 4 Quarters)
# ============================================================
print(f"\n{'='*60}")
print("GROSS MARGINS (Last 4 Quarters)")
print(f"{'='*60}")

# Check if both revenue and gross profit data exist
if 'Total Revenue' in incomeStatement.index and 'Gross Profit' in incomeStatement.index:
    # Get all revenue values
    allRevenue = incomeStatement.loc['Total Revenue']

    # Get all gross profit values
    allGrossProfit = incomeStatement.loc['Gross Profit']

    # Sort both by date - most recent first
    allRevenue = allRevenue.sort_index(ascending=False)
    allGrossProfit = allGrossProfit.sort_index(ascending=False)

    # Loop through last 4 quarters
    for i in range(4):
        if i < len(allRevenue):
            # Get revenue for this quarter
            quarterRevenue = allRevenue.iloc[i]

            # Get gross profit for this quarter
            quarterGrossProfit = allGrossProfit.iloc[i]

            # Calculate gross margin percentage
            grossMarginPercentage = (quarterGrossProfit / quarterRevenue) * 100

            # Print result
            print(f"Q{i+1}: {grossMarginPercentage:.2f}%")

# ============================================================
# EARNINGS SURPRISE HISTORY
# ============================================================
print(f"\n{'='*60}")
print("EARNINGS SURPRISE HISTORY")
print(f"{'='*60}")

# Get earnings dates data
earningsData = stock.earnings_dates

# Check if earnings data exists
if earningsData is not None and not earningsData.empty:
    # Sort by date - most recent first
    earningsData = earningsData.sort_index(ascending=False)

    # Counter to track how many earnings we've printed
    earningsCount = 0

    # Loop through all earnings dates
    for date, row in earningsData.iterrows():
        # Stop after 4 earnings
        if earningsCount >= 4:
            break

        # Check if both reported and estimated EPS exist
        if 'Reported EPS' in row and 'EPS Estimate' in row:
            reportedEps = row['Reported EPS']
            estimatedEps = row['EPS Estimate']

            # Check if values are not NaN (NaN != NaN is True)
            if reportedEps == reportedEps and estimatedEps == estimatedEps:
                # Calculate surprise (difference between reported and estimated)
                surpriseAmount = reportedEps - estimatedEps

                # Calculate surprise percentage
                if estimatedEps != 0:
                    surprisePercentage = (surpriseAmount / abs(estimatedEps)) * 100
                else:
                    surprisePercentage = 0

                # Format date
                dateString = date.strftime('%Y-%m-%d')

                # Print results
                print(f"{dateString}:")
                print(f"  Reported EPS: ${reportedEps:.2f}")
                print(f"  Estimated EPS: ${estimatedEps:.2f}")
                print(f"  Surprise: {surprisePercentage:.2f}%")
                print()

                # Increment counter
                earningsCount += 1

# ============================================================
# SHORT INTEREST
# ============================================================
print(f"{'='*60}")
print("SHORT INTEREST")
print(f"{'='*60}")

# Get stock info
stockInfo = stock.info

# Check and print short percent of float
if 'shortPercentOfFloat' in stockInfo:
    shortPercent = stockInfo['shortPercentOfFloat'] * 100
    print(f"Short % of Float: {shortPercent:.2f}%")

# Check and print shares short
if 'sharesShort' in stockInfo:
    sharesShort = stockInfo['sharesShort']
    print(f"Shares Short: {sharesShort:,}")

# Check and print days to cover (short ratio)
if 'shortRatio' in stockInfo:
    daysToCover = stockInfo['shortRatio']
    print(f"Days to Cover: {daysToCover:.2f}")

# ============================================================
# EARNINGS DATES
# ============================================================
print(f"\n{'='*60}")
print("EARNINGS DATES")
print(f"{'='*60}")

# Check if earnings data exists
if earningsData is not None:
    # Find previous earnings date (most recent with reported EPS)
    for date, row in earningsData.iterrows():
        if 'Reported EPS' in row:
            reported = row['Reported EPS']
            # Check if reported EPS is not NaN (has been reported)
            if reported == reported:  # NaN != NaN, so this checks if it's a real number
                previousEarningsDate = date.strftime('%Y-%m-%d')
                print(f"Previous Earnings: {previousEarningsDate}")
                break

    # Find next earnings date (future date with no reported EPS)
    for date, row in earningsData.iterrows():
        if 'Reported EPS' in row:
            reported = row['Reported EPS']
            # Check if reported EPS is NaN (hasn't been reported yet)
            if reported != reported:  # This is True when value is NaN
                nextEarningsDate = date.strftime('%Y-%m-%d')
                print(f"Next Earnings: {nextEarningsDate}")
                break

print(f"\n{'='*60}\n")
