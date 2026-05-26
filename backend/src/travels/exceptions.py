from fastapi import HTTPException, status


class TravelNotFound(HTTPException):
    def __init__(self, country_code: str | None = None):
        detail = "Travel not found"
        if country_code:
            detail = f"Travel for '{country_code}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class TravelConflict(HTTPException):
    def __init__(self, country_code: str | None = None):
        detail = f"Travel for '{country_code}' already exists" if country_code else "Travel already exists"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )
