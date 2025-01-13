from amberelectric.models.actual_interval import ActualInterval
from amberelectric.models.channel import ChannelType
from amberelectric.models.current_interval import CurrentInterval
from amberelectric.models.forecast_interval import ForecastInterval
from amberelectric.models.price_descriptor import PriceDescriptor

def format_cents_to_dollars(cents: float) -> float:
    """Return a formatted conversion from cents to dollars."""
    return round(cents / 100, 4)

def friendly_channel_type(channel_type: str) -> str:
    """Return a human readable version of the channel type."""
    if channel_type == "controlled_load":
        return "Controlled Load"
    if channel_type == "feed_in":
        return "Feed In"
    return "General"

def is_current(interval: ActualInterval | CurrentInterval | ForecastInterval) -> bool:
    """Return true if the supplied interval is a CurrentInterval."""
    return isinstance(interval, CurrentInterval)

def is_actual(interval: ActualInterval | CurrentInterval | ForecastInterval) -> bool:
    """Return true if the supplied interval is a CurrentInterval."""
    return isinstance(interval, ActualInterval)

def is_forecast(interval: ActualInterval | CurrentInterval | ForecastInterval) -> bool:
    """Return true if the supplied interval is a ForecastInterval."""
    return isinstance(interval, ForecastInterval)


def is_general(interval: ActualInterval | CurrentInterval | ForecastInterval) -> bool:
    """Return true if the supplied interval is on the general channel."""
    return interval.channel_type == ChannelType.GENERAL


def is_controlled_load(
    interval: ActualInterval | CurrentInterval | ForecastInterval,
) -> bool:
    """Return true if the supplied interval is on the controlled load channel."""
    return interval.channel_type == ChannelType.CONTROLLEDLOAD


def is_feed_in(interval: ActualInterval | CurrentInterval | ForecastInterval) -> bool:
    """Return true if the supplied interval is on the feed in channel."""
    return interval.channel_type == ChannelType.FEEDIN


def normalize_descriptor(descriptor: PriceDescriptor | None) -> str | None:
    """Return the snake case versions of descriptor names. Returns None if the name is not recognized."""
    if descriptor is None:
        return None
    if descriptor.value == "spike":
        return "spike"
    if descriptor.value == "high":
        return "high"
    if descriptor.value == "neutral":
        return "neutral"
    if descriptor.value == "low":
        return "low"
    if descriptor.value == "veryLow":
        return "very_low"
    if descriptor.value == "extremelyLow":
        return "extremely_low"
    if descriptor.value == "negative":
        return "negative"
    return None
