import logging
from app.data_sources.cbsl.service import CBSLService
from app.validation.validator import DataValidator

logger = logging.getLogger(__name__)


class CBSLPipeline:

    def __init__(self):
        self.cbsl_service = CBSLService()

    def run(self) -> int:
        logger.info("CBSL Pipeline: Fetching CBSL indicators...")
        df = self.cbsl_service.get_macro_indicators()
        if df.empty:
            logger.warning("No CBSL data fetched.")
            return 0

        # Validate CBSL data quality
        report = DataValidator.validate_cbsl_data(df)
        if not report["is_valid"]:
            logger.error(f"Validation failed for CBSL data: {report['errors']}")
            raise ValueError(f"CBSL validation failed: {report['errors']}")

        return len(df)
