"""
Enhanced Backend Services for ZeroSite Expert v3

These services provide improved algorithms for:
- Geocoding (mock)
- Transaction generation (dynamic)
- Price adjustment (4-factor weighted)
- Confidence scoring (4-factor weighted)

To use in existing code:
    from backend.services.geocoding import EnhancedGeocodingService
    from backend.services.transaction_generator import EnhancedTransactionGenerator
    from backend.services.price_adjuster import EnhancedPriceAdjuster
    from backend.services.confidence_calculator import EnhancedConfidenceCalculator
"""

__version__ = "1.0.0"
__all__ = [
    "EnhancedGeocodingService",
    "EnhancedTransactionGenerator",
    "EnhancedPriceAdjuster",
    "EnhancedConfidenceCalculator"
]
