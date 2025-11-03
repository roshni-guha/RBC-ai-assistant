"""
SEC Data Fetcher
Uses SEC Edgar API to fetch quarterly financial data
"""

import requests
import json
from typing import Dict, List, Optional


class SecDataFetcher:
    """Fetch financial data from SEC Edgar API"""

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.baseUrl = "https://data.sec.gov"
        # SEC requires a User-Agent header
        self.headers = {
            'User-Agent': 'Research Analyst research@example.com',
            'Accept-Encoding': 'gzip, deflate'
        }
        self.cik = None
        self.companyFacts = None

    def getCik(self) -> Optional[str]:
        """Get CIK (Central Index Key) for the ticker"""
        try:
            # Use SEC submissions endpoint to search by ticker
            # This is more reliable than the tickers JSON file
            submissionsUrl = f"{self.baseUrl}/submissions/CIK{self.ticker}.json"

            # Try direct ticker lookup first
            try:
                response = requests.get(submissionsUrl, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    self.cik = str(data['cik']).zfill(10)
                    return self.cik
            except:
                pass

            # If that fails, use a known CIK mapping for common tickers
            # You can expand this list as needed
            cikMapping = {
                'AAPL': '0000320193',
                'MSFT': '0000789019',
                'GOOGL': '0001652044',
                'GOOG': '0001652044',
                'TSLA': '0001318605',
                'META': '0001326801',
                'AMZN': '0001018724',
                'NVDA': '0001045810',
                'PLTR': '0001321655',
            }

            if self.ticker in cikMapping:
                self.cik = cikMapping[self.ticker]
                return self.cik

            print(f"Ticker {self.ticker} not found. Please add CIK mapping.")
            return None

        except Exception as e:
            print(f"Error getting CIK: {e}")
            return None

    def getCompanyFacts(self) -> Optional[Dict]:
        """Get all company facts from SEC"""
        if not self.cik:
            self.getCik()

        if not self.cik:
            return None

        try:
            # Get company facts JSON
            factsUrl = f"{self.baseUrl}/api/xbrl/companyfacts/CIK{self.cik}.json"
            response = requests.get(factsUrl, headers=self.headers)
            response.raise_for_status()

            self.companyFacts = response.json()
            return self.companyFacts

        except Exception as e:
            print(f"Error getting company facts: {e}")
            return None

    def getQuarterlyData(self, conceptName: str, units: str = "USD") -> List[Dict]:
        """
        Get quarterly data for a specific financial concept

        Args:
            conceptName: XBRL concept name (e.g., 'Revenues', 'NetIncomeLoss')
            units: Unit of measurement (default: 'USD')

        Returns:
            List of quarterly data points
        """
        if not self.companyFacts:
            self.getCompanyFacts()

        if not self.companyFacts:
            return []

        try:
            # Navigate to the concept in the facts
            usgaap = self.companyFacts.get('facts', {}).get('us-gaap', {})

            if conceptName not in usgaap:
                print(f"Concept '{conceptName}' not found")
                return []

            concept = usgaap[conceptName]

            # Get units data
            if units not in concept.get('units', {}):
                print(f"Units '{units}' not found for {conceptName}")
                return []

            allData = concept['units'][units]

            # Filter for quarterly data only (10-Q filings)
            quarterlyData = []
            for item in allData:
                # Check if it's quarterly data
                if item.get('form') == '10-Q' or item.get('fp') in ['Q1', 'Q2', 'Q3']:
                    quarterlyData.append({
                        'date': item.get('end'),
                        'fiscalYear': item.get('fy'),
                        'fiscalPeriod': item.get('fp'),
                        'value': item.get('val'),
                        'filed': item.get('filed'),
                        'form': item.get('form')
                    })

            # Sort by date - most recent first
            quarterlyData.sort(key=lambda x: x['date'], reverse=True)

            return quarterlyData

        except Exception as e:
            print(f"Error getting quarterly data for {conceptName}: {e}")
            return []

    def getSalesGrowth(self, numQuarters: int = 3) -> Dict:
        """Get year-over-year sales growth for last N quarters"""
        # Try different revenue concept names
        revenueConcepts = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
                          'SalesRevenueNet', 'RevenueFromContractWithCustomer']

        quarterlyRevenue = []
        for concept in revenueConcepts:
            quarterlyRevenue = self.getQuarterlyData(concept)
            if quarterlyRevenue:
                break

        if not quarterlyRevenue:
            return {"error": "No revenue data found"}

        results = {}

        for i in range(numQuarters):
            if i >= len(quarterlyRevenue):
                break

            # Find matching quarter from previous year
            currentQuarter = quarterlyRevenue[i]
            currentFiscalPeriod = currentQuarter['fiscalPeriod']
            currentFiscalYear = currentQuarter['fiscalYear']

            # Look for same period previous year
            priorYearQuarter = None
            for q in quarterlyRevenue:
                if (q['fiscalPeriod'] == currentFiscalPeriod and
                    q['fiscalYear'] == currentFiscalYear - 1):
                    priorYearQuarter = q
                    break

            if priorYearQuarter:
                currentRevenue = currentQuarter['value']
                priorRevenue = priorYearQuarter['value']

                yoyGrowth = ((currentRevenue - priorRevenue) / priorRevenue) * 100

                results[f"Q{i+1} - FY{currentFiscalYear} {currentFiscalPeriod}"] = {
                    'date': currentQuarter['date'],
                    'currentRevenue': f"${currentRevenue:,.0f}",
                    'priorYearRevenue': f"${priorRevenue:,.0f}",
                    'yoyGrowth': f"{yoyGrowth:.2f}%"
                }

        return results if results else {"error": "Insufficient data for Y/Y comparison"}

    def getEarningsGrowth(self, numQuarters: int = 3) -> Dict:
        """Get year-over-year earnings growth for last N quarters"""
        # Try different earnings concept names
        earningsConcepts = ['NetIncomeLoss', 'ProfitLoss', 'NetIncomeLossAvailableToCommonStockholdersBasic']

        quarterlyEarnings = []
        for concept in earningsConcepts:
            quarterlyEarnings = self.getQuarterlyData(concept)
            if quarterlyEarnings:
                break

        if not quarterlyEarnings:
            return {"error": "No earnings data found"}

        results = {}

        for i in range(numQuarters):
            if i >= len(quarterlyEarnings):
                break

            currentQuarter = quarterlyEarnings[i]
            currentFiscalPeriod = currentQuarter['fiscalPeriod']
            currentFiscalYear = currentQuarter['fiscalYear']

            # Look for same period previous year
            priorYearQuarter = None
            for q in quarterlyEarnings:
                if (q['fiscalPeriod'] == currentFiscalPeriod and
                    q['fiscalYear'] == currentFiscalYear - 1):
                    priorYearQuarter = q
                    break

            if priorYearQuarter:
                currentEarnings = currentQuarter['value']
                priorEarnings = priorYearQuarter['value']

                # Handle negative earnings
                if priorEarnings != 0:
                    yoyGrowth = ((currentEarnings - priorEarnings) / abs(priorEarnings)) * 100
                else:
                    yoyGrowth = 0

                results[f"Q{i+1} - FY{currentFiscalYear} {currentFiscalPeriod}"] = {
                    'date': currentQuarter['date'],
                    'currentEarnings': f"${currentEarnings:,.0f}",
                    'priorYearEarnings': f"${priorEarnings:,.0f}",
                    'yoyGrowth': f"{yoyGrowth:.2f}%"
                }

        return results if results else {"error": "Insufficient data for Y/Y comparison"}

    def getEbitdaMargins(self, numQuarters: int = 3) -> Dict:
        """Get EBITDA margins for last N quarters"""
        # EBITDA is not always directly reported, may need to calculate
        # For now, try to get it directly
        ebitdaConcepts = ['EBITDA', 'EarningsBeforeInterestTaxesDepreciationAndAmortization']

        quarterlyEbitda = []
        for concept in ebitdaConcepts:
            quarterlyEbitda = self.getQuarterlyData(concept)
            if quarterlyEbitda:
                break

        # Also get revenue for margin calculation
        revenueConcepts = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax']
        quarterlyRevenue = []
        for concept in revenueConcepts:
            quarterlyRevenue = self.getQuarterlyData(concept)
            if quarterlyRevenue:
                break

        if not quarterlyEbitda or not quarterlyRevenue:
            return {"note": "EBITDA data not directly available in SEC filings. This metric may need to be calculated from other line items."}

        results = {}

        for i in range(numQuarters):
            if i >= len(quarterlyEbitda):
                break

            ebitdaQuarter = quarterlyEbitda[i]

            # Find matching revenue quarter
            matchingRevenue = None
            for revQuarter in quarterlyRevenue:
                if (revQuarter['date'] == ebitdaQuarter['date'] and
                    revQuarter['fiscalPeriod'] == ebitdaQuarter['fiscalPeriod']):
                    matchingRevenue = revQuarter
                    break

            if matchingRevenue:
                ebitda = ebitdaQuarter['value']
                revenue = matchingRevenue['value']

                if revenue != 0:
                    margin = (ebitda / revenue) * 100

                    results[f"Q{i+1} - {ebitdaQuarter['date']}"] = {
                        'ebitda': f"${ebitda:,.0f}",
                        'revenue': f"${revenue:,.0f}",
                        'ebitdaMargin': f"{margin:.2f}%"
                    }

        return results if results else {"note": "EBITDA data not available"}

    def printReport(self):
        """Print formatted SEC data report"""
        print(f"\n{'='*60}")
        print(f"SEC DATA REPORT: {self.ticker}")
        print(f"{'='*60}")

        if not self.cik:
            self.getCik()

        print(f"CIK: {self.cik}")
        print()

        # Sales Growth
        print(f"{'='*60}")
        print("SALES GROWTH Y/Y (from SEC filings)")
        print(f"{'='*60}")
        salesGrowth = self.getSalesGrowth(3)
        self._printDict(salesGrowth)

        # Earnings Growth
        print(f"\n{'='*60}")
        print("EARNINGS GROWTH Y/Y (from SEC filings)")
        print(f"{'='*60}")
        earningsGrowth = self.getEarningsGrowth(3)
        self._printDict(earningsGrowth)

        # EBITDA Margins
        print(f"\n{'='*60}")
        print("EBITDA MARGINS (from SEC filings)")
        print(f"{'='*60}")
        ebitdaMargins = self.getEbitdaMargins(3)
        self._printDict(ebitdaMargins)

        print(f"\n{'='*60}\n")

    def _printDict(self, data: Dict, indent: int = 0):
        """Helper to print nested dictionaries"""
        if not isinstance(data, dict):
            print(f"{' '*indent}{data}")
            return

        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{' '*indent}{key}:")
                self._printDict(value, indent + 2)
            else:
                print(f"{' '*indent}{key}: {value}")


def main():
    """Test the SEC data fetcher"""
    ticker = input("Enter ticker symbol: ").strip().upper()

    fetcher = SecDataFetcher(ticker)
    fetcher.printReport()


if __name__ == "__main__":
    main()
