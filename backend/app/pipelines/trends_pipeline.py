import logging
from app.data_sources.trends.service import TrendsService
from app.validation.validator import DataValidator

logger = logging.getLogger(__name__)


class TrendsPipeline:

    def __init__(self):
        self.trends_service = TrendsService()

    def run(self, keyword: str = "CSE") -> int:
        logger.info(f"Google Trends Pipeline: Fetching search interest for '{keyword}'...")
        df = self.trends_service.get_search_trends(keyword)
        if df.empty:
            logger.warning(f"No Google Trends data fetched for keyword: {keyword}")
            return 0

        # Validate Trends data
        report = DataValidator.validate_trends_data(df)
        if not report["is_valid"]:
            logger.error(f"Validation failed for Google Trends: {report['errors']}")
            raise ValueError(f"Google Trends validation failed: {report['errors']}")

        return len(df)
