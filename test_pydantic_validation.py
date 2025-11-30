"""Quick test to see if Pydantic already validates ask types."""

from pydantic import BaseModel, ValidationError

from werk24.models.v1.ask import W24AskTitleBlock
from werk24.models.v2.asks import AskBalloons
from werk24.models.v2.internal import TechreadRequest

# Test 1: Valid asks should work
print("Test 1: Valid asks")
try:
    request = TechreadRequest(asks=[W24AskTitleBlock(), AskBalloons()], max_pages=5)
    print(f"✓ Valid asks accepted: {len(request.asks)} asks")
except ValidationError as e:
    print(f"✗ Validation error: {e}")

print()

# Test 2: Invalid ask type
print("Test 2: Invalid ask type")


class InvalidAsk(BaseModel):
    ask_type: str = "INVALID_TYPE"


try:
    request = TechreadRequest(asks=[InvalidAsk()], max_pages=5)
    print(f"✗ Invalid ask was accepted (shouldn't happen)")
except ValidationError as e:
    print(f"✓ Pydantic caught the invalid ask:")
    print(f"  {e.errors()[0]['msg']}")

print()

# Test 3: Empty asks list
print("Test 3: Empty asks list")
try:
    request = TechreadRequest(asks=[], max_pages=5)
    print(f"✓ Empty asks list accepted (Pydantic doesn't validate list length)")
except ValidationError as e:
    print(f"✗ Validation error: {e}")
