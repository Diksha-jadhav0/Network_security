from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import FutureRiskResponse
from .auth import get_current_user
from ..services.risk_predictor import RiskPredictorService

router = APIRouter(prefix="/api/prediction", tags=["Future Risk Prediction"])

@router.get("/future-risk", response_model=FutureRiskResponse)
def get_future_risk_prediction(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Predict the user's future 24-hour phishing exposure risk based on aggregated historical email behavior.
    """
    result = RiskPredictorService.predict_user_risk(db, current_user.id)
    return FutureRiskResponse(**result)
