import requests


class CSEClient:


    def __init__(self):

        self.base_url = "https://www.cse.lk/api"

        self.headers = {

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

            "Content-Type": "application/x-www-form-urlencoded"

        }



    def get_stock_id(self, symbol: str) -> int:

        """
        Fetch company info summary to resolve the stock's internal ID.
        """

        url = f"{self.base_url}/companyInfoSummery"

        formatted_symbol = symbol if "." in symbol else f"{symbol}.N0000"

        payload = {"symbol": formatted_symbol}


        response = requests.post(url, data=payload, headers=self.headers, timeout=10)

        response.raise_for_status()


        data = response.json()

        stock_id = data.get("reqSymbolInfo", {}).get("id")

        return stock_id



    def get_historical_data(self, stock_id: int, period: str = "5") -> dict:

        """
        Fetch historical daily charts using stockId and period.
        period='5' represents approx. 1 trading year (242 points).
        period='3' represents approx. 1 trading month (20 points).
        """

        url = f"{self.base_url}/companyChartDataByStock"

        payload = {

            "stockId": str(stock_id),

            "period": period

        }

        response = requests.post(url, data=payload, headers=self.headers, timeout=10)

        response.raise_for_status()

        return response.json()
