import yfinance as yf

# Get ticker from user
ticker = input("Enter ticker symbol: ").strip().upper()

# Create stock object
stock = yf.Ticker(ticker)

# Get company info
company_name = stock.info.get('longName', 'N/A')
current_price = stock.info.get('currentPrice', 'N/A')
market_cap = stock.info.get('marketCap', 0)

# Print company info
print(f"\n{'='*60}")
print(f"RESEARCH REPORT: {ticker}")
print(f"{'='*60}")
print(f"Company: {company_name}")
print(f"Price: ${current_price}")
print(f"Market Cap: ${market_cap:,.0f}")

# ============================================================
# SALES GROWTH Y/Y (Last 3 Quarters)
# ============================================================
print(f"\n{'='*60}")
print("SALES GROWTH Y/Y (Last 3 Quarters)")
print(f"{'='*60}")

# Get quarterly income statement data
income_statement = stock.quarterly_income_stmt

# Check if revenue data exists
if 'Total Revenue' in income_statement.index:
    # Get all revenue values
    all_revenue = income_statement.loc['Total Revenue']

    # Sort by date - most recent first
    all_revenue = all_revenue.sort_index(ascending=False)

    # Loop through last 3 quarters
    for i in range(3):
        # Check if we have enough data to compare year-over-year
        # We need data from 4 quarters ago (1 year ago)
        if i + 4 < len(all_revenue):
            # Get current quarter revenue
            current_quarter_revenue = all_revenue.iloc[i]

            # Get revenue from same quarter last year (4 quarters ago)
            last_year_revenue = all_revenue.iloc[i + 4]

            # Calculate year-over-year growth percentage
            revenue_change = current_quarter_revenue - last_year_revenue
            growth_percentage = (revenue_change / abs(last_year_revenue)) * 100

            # Get the quarter date
            quarter_date = all_revenue.index[i].strftime('%Y-%m-%d')

            # Print results
            print(f"Quarter {i+1} ({quarter_date}):")
            print(f"  Current Revenue: ${current_quarter_revenue:,.0f}")
            print(f"  Last Year Revenue: ${last_year_revenue:,.0f}")
            print(f"  Y/Y Growth: {growth_percentage:.2f}%")
            print()

# ============================================================
# FREE CASH FLOW GROWTH (Last 4 Quarters)
# ============================================================
print(f"{'='*60}")
print("FREE CASH FLOW GROWTH (Last 4 Quarters)")
print(f"{'='*60}")

# Get quarterly cash flow data
cashflow_statement = stock.quarterly_cashflow

# Check if FCF data exists
if 'Free Cash Flow' in cashflow_statement.index:
    # Get all FCF values
    all_fcf = cashflow_statement.loc['Free Cash Flow']

    # Sort by date - most recent first
    all_fcf = all_fcf.sort_index(ascending=False)

    # Loop through last 4 quarters
    for i in range(4):
        # Check if we have enough data to compare year-over-year
        if i + 4 < len(all_fcf):
            # Get current quarter FCF
            current_quarter_fcf = all_fcf.iloc[i]

            # Get FCF from same quarter last year
            last_year_fcf = all_fcf.iloc[i + 4]

            # Calculate year-over-year growth
            fcf_change = current_quarter_fcf - last_year_fcf
            growth_percentage = (fcf_change / abs(last_year_fcf)) * 100

            # Print results
            print(f"Q{i+1}: ${current_quarter_fcf:,.0f} | Y/Y Growth: {growth_percentage:.2f}%")

# ============================================================
# GROSS MARGINS (Last 4 Quarters)
# ============================================================
print(f"\n{'='*60}")
print("GROSS MARGINS (Last 4 Quarters)")
print(f"{'='*60}")

# Check if both revenue and gross profit data exist
if 'Total Revenue' in income_statement.index and 'Gross Profit' in income_statement.index:
    # Get all revenue values
    all_revenue = income_statement.loc['Total Revenue']

    # Get all gross profit values
    all_gross_profit = income_statement.loc['Gross Profit']

    # Sort both by date - most recent first
    all_revenue = all_revenue.sort_index(ascending=False)
    all_gross_profit = all_gross_profit.sort_index(ascending=False)

    # Loop through last 4 quarters
    for i in range(4):
        if i < len(all_revenue):
            # Get revenue for this quarter
            quarter_revenue = all_revenue.iloc[i]

            # Get gross profit for this quarter
            quarter_gross_profit = all_gross_profit.iloc[i]

            # Calculate gross margin percentage
            gross_margin_percentage = (quarter_gross_profit / quarter_revenue) * 100

            # Print result
            print(f"Q{i+1}: {gross_margin_percentage:.2f}%")

# ============================================================
# EARNINGS SURPRISE HISTORY
# ============================================================
print(f"\n{'='*60}")
print("EARNINGS SURPRISE HISTORY")
print(f"{'='*60}")

# Get earnings dates data
earnings_data = stock.earnings_dates

# Check if earnings data exists
if earnings_data is not None and not earnings_data.empty:
    # Sort by date - most recent first
    earnings_data = earnings_data.sort_index(ascending=False)

    # Counter to track how many earnings we've printed
    earnings_count = 0

    # Loop through all earnings dates
    for date, row in earnings_data.iterrows():
        # Stop after 4 earnings
        if earnings_count >= 4:
            break

        # Check if both reported and estimated EPS exist
        if 'Reported EPS' in row and 'EPS Estimate' in row:
            reported_eps = row['Reported EPS']
            estimated_eps = row['EPS Estimate']

            # Check if values are not NaN (NaN != NaN is True)
            if reported_eps == reported_eps and estimated_eps == estimated_eps:
                # Calculate surprise (difference between reported and estimated)
                surprise_amount = reported_eps - estimated_eps

                # Calculate surprise percentage
                if estimated_eps != 0:
                    surprise_percentage = (surprise_amount / abs(estimated_eps)) * 100
                else:
                    surprise_percentage = 0

                # Format date
                date_string = date.strftime('%Y-%m-%d')

                # Print results
                print(f"{date_string}:")
                print(f"  Reported EPS: ${reported_eps:.2f}")
                print(f"  Estimated EPS: ${estimated_eps:.2f}")
                print(f"  Surprise: {surprise_percentage:.2f}%")
                print()

                # Increment counter
                earnings_count += 1

# ============================================================
# SHORT INTEREST
# ============================================================
print(f"{'='*60}")
print("SHORT INTEREST")
print(f"{'='*60}")

# Get stock info
stock_info = stock.info

# Check and print short percent of float
if 'shortPercentOfFloat' in stock_info:
    short_percent = stock_info['shortPercentOfFloat'] * 100
    print(f"Short % of Float: {short_percent:.2f}%")

# Check and print shares short
if 'sharesShort' in stock_info:
    shares_short = stock_info['sharesShort']
    print(f"Shares Short: {shares_short:,}")

# Check and print days to cover (short ratio)
if 'shortRatio' in stock_info:
    days_to_cover = stock_info['shortRatio']
    print(f"Days to Cover: {days_to_cover:.2f}")

# ============================================================
# EARNINGS DATES
# ============================================================
print(f"\n{'='*60}")
print("EARNINGS DATES")
print(f"{'='*60}")

# Check if earnings data exists
if earnings_data is not None:
    # Find previous earnings date (most recent with reported EPS)
    for date, row in earnings_data.iterrows():
        if 'Reported EPS' in row:
            reported = row['Reported EPS']
            # Check if reported EPS is not NaN (has been reported)
            if reported == reported:  # NaN != NaN, so this checks if it's a real number
                previous_earnings_date = date.strftime('%Y-%m-%d')
                print(f"Previous Earnings: {previous_earnings_date}")
                break

    # Find next earnings date (future date with no reported EPS)
    for date, row in earnings_data.iterrows():
        if 'Reported EPS' in row:
            reported = row['Reported EPS']
            # Check if reported EPS is NaN (hasn't been reported yet)
            if reported != reported:  # This is True when value is NaN
                next_earnings_date = date.strftime('%Y-%m-%d')
                print(f"Next Earnings: {next_earnings_date}")
                break

print(f"\n{'='*60}\n")
