from datetime import datetime, timezone, timedelta

# Indian Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now() -> datetime:
    """Get current datetime in Indian Standard Time"""
    return datetime.now(IST)

def get_ist_timestamp() -> str:
    """Get current timestamp as ISO string in Indian Standard Time"""
    return get_ist_now().isoformat()

def utc_to_ist(utc_datetime: datetime) -> datetime:
    """Convert UTC datetime to IST"""
    if utc_datetime.tzinfo is None:
        # Assume UTC if no timezone info
        utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    return utc_datetime.astimezone(IST)

def ist_to_utc(ist_datetime: datetime) -> datetime:
    """Convert IST datetime to UTC"""
    if ist_datetime.tzinfo is None:
        # Assume IST if no timezone info
        ist_datetime = ist_datetime.replace(tzinfo=IST)
    return ist_datetime.astimezone(timezone.utc)

def format_ist_timestamp(dt: datetime = None) -> str:
    """Format datetime as IST timestamp string"""
    if dt is None:
        dt = get_ist_now()
    elif dt.tzinfo is None:
        # Assume UTC and convert to IST
        dt = dt.replace(tzinfo=timezone.utc).astimezone(IST)
    elif dt.tzinfo != IST:
        # Convert to IST
        dt = dt.astimezone(IST)
    
    return dt.isoformat()

def parse_timestamp_to_ist(timestamp_str: str) -> datetime:
    """Parse timestamp string and convert to IST"""
    try:
        # Parse the timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # Convert to IST
        if dt.tzinfo is None:
            # Assume UTC
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt.astimezone(IST)
    except Exception:
        # If parsing fails, return current IST time
        return get_ist_now()

def format_timestamp_for_api(timestamp_str: str) -> str:
    """Format timestamp string for API responses in IST"""
    try:
        # Parse and convert to IST
        ist_dt = parse_timestamp_to_ist(timestamp_str)
        
        # Format as readable IST timestamp
        return ist_dt.strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception:
        # If formatting fails, return the original string
        return timestamp_str